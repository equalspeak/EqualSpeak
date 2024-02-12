# class parse_vertex:

#     def __init__(self, data) -> None:
#         self.data = data 
#         self.name = data.__hash__()
#         self.children = None

#     def __repr__(self) -> str:
#         return str(self.data)
    
#     def __eq__(self, __value: object) -> bool:
#         pass

class parse_tree:

    def __init__(self, root) -> None:
        self.root = root
        self.vertices = {root}
        self.edges = {}

    def __repr__(self) -> str:
        pass