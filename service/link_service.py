from typing import Union

from backend.model import Models
from backend.utils.enums import Category, FileType
from backend.utils.objects import Link, Folder, Ownership
from backend.utils.exception import CustomException
from backend.database.query import BlockQuery, SnodeQuery, GroupQuery


class LinkService():
    def __init__(self, models: Models, config):
        self.model_link = models.link
        self.model_group = models.group
        self.config = config
        self.category = Category.Link

    def register_files(self, meta: dict, data: list) -> (int, list[int]):
        """
        해당 폴더(snode) 아래에 전달된 링크, 폴더들을 업로드한다.
            - 같은 이름의 폴더는 생성할 수 없다.
            - 블록 생성 -> 노드 생성 -> 블록 할당
        @param meta: gid, snode, owner로 구성된 딕셔너리
        @param data: type, content로 구성된 딕셔너리
        @return: gid와 등록한 파일들의 snode 목록
        """
        # 객체롤 만든다.
        ownership, parent = self.parse_meta(meta)
        files = self.parse_data(data)

        # 유효성검사: 링크를 루트 폴더에 생성하려는 경우
        # 유효성검사: 루트 폴더에 여러 폴더를 한꺼번에 생성하려는 경우
        print(parent, files)
        if parent == 1:
            if any(file.get_type() == FileType.Link for file in files):
                raise CustomException(1, False, "링크는 반드시 속한 그룹과 폴더가 존재해야 합니다.")
            if len(files) > 1:
                raise CustomException(3, is_global=False, message="루트 폴더에는 한꺼번에 여러 폴더를 생성할 수 없습니다.")

        # 부모 노드 조회
        parent_node = self.model_link.get_snode(parent)
        # 추가할 블럭, 노드 생성
        blocks = []; snodes = []
        for file in files:
            snode, block = self.model_link.parse_file(file, parent_node.block, ownership)
            snodes.append(snode)
            blocks.append(block)

            if file.get_type() == FileType.Folder:
                base_blocks = self.model_link.create_base_blocks(
                    snode.block, snode.snode, parent_node.snode
                )
                blocks.extend(base_blocks)

        # gid가 없으면 그룹 생성
        if ownership.gid is None:
            ownership.gid = self.model_group.create_group(ownership.owner)
        # DB에 저장
        self.model_link.insert_snodes(snodes)
        self.model_link.insert_blocks(blocks)

        # gid와 snode 목록 반환
        snode_nums = list(map(lambda s: s.snode, snodes))
        return ownership.gid, snode_nums

    def read_files(self, node_num: int) -> list[dict]:
        """
        폴더이면 하위 폴더/링크 목록을, 링크이면 링크 정보를 가져온다.
        @param snode: 조회할 snode
        @return: 파일 객체 목록
        """
        result = []
        snode = self.model_link.get_snode(node_num)
        if snode.type == FileType.Link:
            result.append(self.model_link.read_link(snode))
        elif snode.type == FileType.Folder:
            result.extend(self.model_link.read_folder(snode))

        if not result:
            raise CustomException(2, is_global=False, message="snode를 읽지 못함")

        # dict {meta, content}로 변환
        result = list(map(lambda x: {
            'meta': {'snode': x.snode, 'type': x.type, 'gid': snode.ownership.gid},
            'content': x.to_content_dict()
        }, result))
        return result

    def read_by_email(self, email: str):
        """
         email에 공유된 공유폴더들을 모두 불러온다
         TODO: 서브폴더 지원 시 로직 수정 필요
        @param email: 조회할 이메일 주소
        @return: list[Folder]
        """
        groups = self.model_group.get_groups(GroupQuery(members=email))
        gids = [group.gid for group in groups]
        if not groups:
            return []

        query = SnodeQuery(gid=gids, type=FileType.Folder)
        snodes = self.model_link.get_snodes(query)
        if not snodes:
            return []

        query = BlockQuery(block=1, snode=[snode.snode for snode in snodes])
        blocks = self.model_link.get_blocks(query)

        # 순서 맞추기
        snodes.sort(key=lambda x: x.snode)
        blocks.sort(key=lambda x: x.snode)

        result = []
        for i in range(len(snodes)):
            result.append({
                'meta': {'snode': snodes[i].snode, 'type': snodes[i].type.value, 'gid': snodes[i].ownership.gid},
                'content': blocks[i].to_content_dict()
            })

        return result

    def delete_files(self, nums: list[int]):
        """
        서버에 있는 폴더/링크들을 삭제한다
            - 폴더이면 내부 모든 링크를 삭제한다.
            - 링크이면 자기 자신만 삭제한다.
        @param nums: 삭제할 snode 번호들
        @return: 삭제 성공 여부
        """
        if not nums:
            raise CustomException(2, True)

        try:
            snodes = [self.model_link.get_snode(num) for num in nums]
        except FileNotFoundError as e:
            raise CustomException(code=2, is_global=False, message=e.__str__())

        # 성능을 위해 링크과 폴더 분리
        folders = [snode for snode in snodes if snode.type == FileType.Folder]
        links = [snode for snode in snodes if snode.type == FileType.Link]
        # 루트 폴더이면 그룹도 삭제해야 한다
        # TODO: 서브폴더 지원 시 루트폴더 검사
        gids = [folder.ownership.gid for folder in folders]

        self.model_link.delete_folders(folders)
        self.model_link.delete_links(links)
        self.model_group.delete_groups(gids)

    def move_files(self, snodes: list[int], before: int, after: int):
        """
        폴더/링크를 다른 폴더로 이동한다.
            - 링크이면 자신 블록만 수정한다.
            - 폴더이면 자신 블록과 .. 블록을 수정한다.
        @param snodes: 이동할 폴더/링크 snode 목록
        @param before: 이동 전 폴더 snode
        @param after: 이동 후 폴더 snode
        """
        # Snode 객체로 변환
        try:
            snodes = list(map(lambda x: self.model_link.get_snode(x), snodes))
            snode_before = self.model_link.get_snode(before)
            snode_after = self.model_link.get_snode(after)
        except FileNotFoundError:
            raise CustomException(code=2, is_global=False, message="폴더/링크 Snode 찾기 실패")

        # 자신 블록의 블록번호를 이동할 곳의 블록번호로 수정
        # TODO: 리팩토링 필요
        query = BlockQuery()
        for snode in snodes:
            query.set(block=snode_before.block,
                      snode=snode.snode,
                      name=None)
            update = {'block': snode_after.block}
            self.model_link.update_block(query, update)
            # gid 변경
            self.model_link.update_snode(
                num=snode.snode,
                values={'gid': snode_after.ownership.gid}
            )
            # 폴더이면 추가로 자신의 .. 블록의 snode를 수정
            if snode.type == FileType.Folder:
                query.set(block=snode.block, snode=None, name="..")
                update = {'snode': snode_after.snode}
                self.model_link.update_block(query, update)

    def update_file(self, snode_num: int, update: dict):
        """
         snode에 해당하는 폴더/링크 정보를 수정한다.
           - 폴더 정보: Block > snode + not ., ..
           - 링크 정보: Block > snode
        @param snode_num: 변경할 파일의 Snode
        @param update: 변경할 정보
        """
        try:
            snode = self.model_link.get_snode(snode_num)
        except FileNotFoundError:
            raise CustomException(2, is_global=False)

        # None인 키는 삭제한다.
        for key in update.keys():
            if update[key] is None:
                del update[key]

        query = BlockQuery(snode=snode.snode, own=True)
        self.model_link.update_block(query, update)

    def clear_database(self):
        """
        데이터베이스를 루트폴더, 루트그룹만 남기고 초기화한다.
        """
        self.model_link.clear_snodes()
        self.model_link.clear_blocks()
        self.model_group.clear_groups()

    def parse_meta(self, meta: dict) -> (Ownership, int):
        """
        메타 정보로부터 Ownership 객체와 snode 번호를 만든다.
            - snode가 없다는 것은 최상위 폴더임을 의미한다.
        @param meta: owner, gid, snode로 구성된 딕셔너리
        @return: Ownership과 snode
        """
        gid = meta.get('gid', None)
        owner = meta['owner']
        snode = meta.get('snode', None)

        if not snode:
            snode = 1

        ownership = Ownership(owner=owner, gid=gid)

        return ownership, snode

    def parse_data(self, data: list) -> list[Union[Folder, Link]]:
        """
        데이터 정보로부터 Link, Folder 객체를 생성한다.
        @param data: type, content 항목으로 이루어진 딕셔너리
        @return: Folder 또는 Link의 배열
        """
        result = []
        for file in data:
            type = FileType(file['type'])
            content = file['content']

            parsed = None
            if type == FileType.Link:
                parsed = Link().set_from(content)
            elif type == FileType.Folder:
                parsed = Folder().set_from(content)
            result.append(parsed)

        return result
