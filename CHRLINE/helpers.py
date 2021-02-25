# -*- coding: utf-8 -*-

class Helpers(object):

    def __init__(self):
        pass
    
    def squareMemberIdIsMe(self, squareMemberId):
        if self.can_use_square:
            if squareMemberId in self.squares.get(2, {}).keys():
                return True
            else:
                return False
        else:
            raise Exception('Not support Square')