
class deci_node():
    def __init__(self, lookUpCol):
        self.lookUpCol = lookUpCol
        self.actions = {}
        self.next_node = None
    def add_action(self, key, act):
        self.actions[key] = act

class deci_tree():

    def __init__(self):
        self.root = None
        self.curr = None

    def add_next_attr(self, nextLookUpCol):
        if self.curr:
            self.curr.next_node = deci_node(nextLookUpCol)
            self.curr = self.curr.next_node
            return True
        elif self.root == None:
            self.root = deci_node(nextLookUpCol)
            self.curr = self.root
            return True
        return False

    def add_action(self, val, act):
        self.curr.add_action(val, act)

    def make_decision_based_on_attribute_vector(self, vec):
        if self.root:
            next_attribute = self.root
            while next_attribute != None:
                curr_checking_attribute_value_in_vec = vec[next_attribute.lookUpCol]
                attemp_get_rslt = next_attribute.actions.get(curr_checking_attribute_value_in_vec)
                if attemp_get_rslt:
                    return attemp_get_rslt
                next_attribute = next_attribute.next_node
        return None
def test():
    X = [
        # True/False = 0.9/0.1
        # For Pat, 0.3==None, 0.6==Some, 0.9==Full
        # For Pri, 0.3==$, 0.6==$$, 0.9==$$$
        # For Type, 0.2==French, 0.4==Thai, 0.6==Burger, 0.8==Italian
        # For Est, 0.2 == 0-10, 0.4 == 10-30. 0.6 == 30-60, 0.8 == >60
        #Alt|Bar|Fri|Pat|Pri|Rai|Res|Typ|Est
        [0.9,0.1,0.1,0.6,0.9,0.1,0.9,0.2,0.2],
        [0.9,0.1,0.1,0.9,0.3,0.1,0.1,0.4,0.6],
        [0.1,0.9,0.1,0.6,0.3,0.1,0.1,0.6,0.2],
        [0.9,0.1,0.9,0.9,0.3,0.1,0.1,0.4,0.4],
        [0.9,0.1,0.9,0.9,0.9,0.1,0.9,0.2,0.8],
        [0.1,0.9,0.1,0.6,0.6,0.9,0.9,0.8,0.2],
        [0.1,0.9,0.1,0.3,0.3,0.9,0.1,0.6,0.2],
        [0.1,0.1,0.1,0.6,0.6,0.9,0.9,0.4,0.2],
        [0.1,0.9,0.9,0.9,0.3,0.9,0.1,0.6,0.8],
        [0.9,0.9,0.9,0.9,0.9,0.1,0.9,0.8,0.4],
        [0.1,0.1,0.1,0.3,0.3,0.1,0.1,0.4,0.2],
        [0.9,0.9,0.9,0.9,0.3,0.1,0.1,0.6,0.6]
    ]
    y = [
        [0.9],
        [0.1],
        [0.9],
        [0.9],
        [0.1],
        [0.9],
        [0.1],
        [0.9],
        [0.1],
        [0.1],
        [0.1],
        [0.9]
        ]
    atree = deci_tree()
    atree.add_next_attr(3)
    atree.add_action(0.3, 0.1)
    atree.add_action(0.6, 0.9)

    atree.add_next_attr(4)
    atree.add_action(0.9, 0.1)

    atree.add_next_attr(8)
    atree.add_action(0.4, 0.9)
    atree.add_action(0.8, 0.1)

    atree.add_next_attr(1)
    atree.add_action(0.9, 0.9)
    atree.add_action(0.1, 0.1)

    i = 0
    for vec in X:
        assert atree.make_decision_based_on_attribute_vector(vec) == y[i][0]
        i += 1
    print("Tests are passed.")
if __name__ == "__main__":  
    test()