from backend.database import DataBase
from backend.database.file_system import FileType, Snode, Block
from backend.database.query import BlockQuery, SnodeQuery
from backend.utils.objects import Ownership
from backend.utils.interfaces import IFile
from backend.utils.exception import CustomException
from backend.config import MONGODB_COLLECTIONS as COLS

SNODE = COLS['snode']
BLOCK = COLS['block']

class LinkDAO():
    def __init__(self, db: DataBase):
        self.db = db
        self.snode = db.get_collection(SNODE)
        self.block = db.get_collection(BLOCK)

    def insert_snodes(self, snodes: list[Snode]):
        """
        Snode 객체를 DB에 저장한다.
            TODO:
        @param snodes: 저장할 Snode 객체 배열
        @return: 저장 성공 여부
        """
        query = [snode.to_dict() for snode in snodes]
        self.snode.insert_many(query)

        print("새로운 노드 추가됨:", query)
        return True

    def insert_blocks(self, blocks: list[Block]):
        """
        Block 객체를 DB에 저장한다.
        @param blocks: 저장할 Block 객체
        @return: 저장 성공 여부
        """
        query = [block.to_dict() for block in blocks]
        self.block.insert_many(query)

        print("새로운 블럭 추가됨:", query)
        return True

    def delete_links(self, snodes: list[Snode]):
        """
        링크는 자기 자신의 블럭만 삭제하면 된다.
        """
        snode_nums = [snode.snode for snode in snodes]

        query = { 'snode': {'$in': snode_nums}}

        self.snode.delete_many(query)
        self.block.delete_many(query)

    def delete_folders(self, snodes: list[Snode]):
        """
        폴더는 자신의 블럭 모두를 삭제한다.
        TODO: 서브폴더를 지원하려면 재귀적으로 처리해야 한다.
        """
        snode_nums = [snode.snode for snode in snodes]
        block_nums = [snode.block for snode in snodes]

        query = {'snode': {'$in': snode_nums}}
        self.snode.delete_many(query)
        # TODO: 하위폴더 지원 시 바뀌어야 한다 (dangling 문제)
        query = {
            '$or': [
                {'block': {'$in': block_nums}},
                {'snode': {'$in': snode_nums}}
            ]
        }
        self.block.delete_many(query)

        print(f"snode 삭제함: {snode_nums}")
        print(f"block 삭제함: {block_nums}")

    def create_base_blocks(self, block, current, parent) -> list[Block]:
        """
        자신과 부모 폴더를 나타내는 기본 블럭을 추가한다.
        @param block: 위치할 block 번호
        @param current: 현재폴더 snode 번호
        @param parent: 부모폴더 snode 번호
        @return: None
        """
        parent_folder = Block(parent, block, "..")
        current_folder = Block(current, block, ".")

        return [parent_folder, current_folder]

    def read_folder(self, snode: Snode) -> list[Block]:
        query = {
            'block': snode.block,
            'name': {
                '$nin': ['.', '..']
            }
        }

        cursor = self.block.find(query, {'_id': 0})

        result = []
        for item in cursor:
            block = item['block']
            snode = item['snode']
            result.append(Block(snode, block).of(item))

        print("폴더를 읽었습니다:", list(map(lambda block: block.to_dict(), result)))
        return result

    def read_link(self, snode: Snode):
        query = {
            'block': snode.block,
            'snode': snode.snode
        }

        result = self.block.find_one(query, {'_id': 0})
        if not result:
            raise CustomException(2, is_global=False, message=f"링크읽기 실패 {snode.to_dict()}")

        print("링크를 읽었습니다:", result)
        return result

    def get_snodes(self, query: SnodeQuery) -> list[Snode]:
        query = query.to_dict()
        cursor = self.snode.find(query)

        snodes = []
        for raw in cursor:
            snodes.append(Snode.of(raw))

        print("Snode를 읽었습니다:", snodes)
        return snodes

    def get_snode(self, num: int) -> Snode:
        """
        해당하는 번호의 Snode를 찾는다.
            - TODO: 조회한 snode가 존재하지 않는 경우
        """
        query = {'snode': num}
        snode_dict = self.snode.find_one(query)
        if not snode_dict:
            raise FileNotFoundError(f"Snode {num} 찾기 실패")

        print(f"Snode 읽음: {snode_dict}")
        return Snode.of(snode_dict)

    def get_blocks(self, query: BlockQuery) -> list[Block]:
        """
        블럭번호, Snode 번호, 이름으로 블럭을 찾는다. (and 조건)
        @param query: BlockQuery 객체
        @return: 탐색한 블럭 목록
        """
        blocks = []
        query = query.to_dict()
        filter = {'_id': 0}

        cursor = self.block.find(query, filter)
        for block in cursor:
            snode = block['snode']
            found = Block(snode=snode).of(block)
            blocks.append(found)

        print(f"블럭을 읽었습니다: {blocks}, 쿼리: {query}")
        return blocks

    def update_snode(self, num: int, values: dict):
        query =  {'snode': num}
        update = { '$set': values }
        result = self.snode.update_one(query, update)
        if result.modified_count <= 0:
            raise CustomException(4, is_global=False)

        print(f"Snode 수정됨: {num}, {result.modified_count}")

    def update_block(self, query: BlockQuery, values: dict):
        """
        해당하는 Block을 찾아 내용을 변경한다.
        @param query: BlockQuery 객체
        @param values: 업데이트할 값
        """
        update = {'$set': values}
        result = self.block.update_one(filter=query.to_dict(), update=update)
        if result.modified_count == 0:
            raise CustomException(4, is_global=False)

        print(f"블록 수정됨: {query.to_dict()}, {result.modified_count}")

    def clear_snodes(self):
        """
        Snode 콜렉션을 초기화한다.
            - 1번 snode만 남긴다
        """
        root_node = Snode(type=FileType.Folder,
                          ownership=Ownership('Linkit', 1),
                          snode=1,
                          block=1)

        self.snode.delete_many({})
        self.insert_snodes([root_node])

    def is_root_folder(self, snode: int) -> bool:
        """
        서브폴더가 아닌 최상위 폴더인지 검사한다
            - snode와 이름 '..'으로 검색한 block의 snode가 1이면 최상위이다
        @param snode: 검사할 폴더의 snode 번호
        @return: bool
        """
        query = BlockQuery(block=None, snode=snode, name="..").to_dict()
        block_dict = self.block.find_one(query)

        return block_dict['snode'] == 1

    def clear_blocks(self):
        """
        Block 콜렉션을 초기화한다.
          - 루트 폴더의 현재 폴더 블럭만 남긴다
        """
        root_block = Block(1, 1, ".")
        self.block.delete_many({})
        self.insert_blocks([root_block])

    def parse_file(self, file: IFile, parent_block: int, ownership: Ownership) -> (Snode, Block):
        """
        링크나 폴더를 표현하는 Block, Snode로 변환한다.
            - 폴더이면 snode의 블럭은 새로 할당된다.
            - 링크이면 snode의 블럭은 현재 블럭을 가리킨다.
        @param file: 변환할 파일
        @param parent_block: 부모의 블럭 번호 (위치할 블럭)
        @param ownership: 자신의 소유권
        @return: 자신의 Snode와 Block
        """
        type = file.get_type()
        block = parent_block if type == FileType.Link else None

        my_snode = Snode(file.get_type(), ownership, block=block)
        my_block = Block(my_snode.snode, parent_block).of(file)

        return my_snode, my_block
