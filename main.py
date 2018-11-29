
def csv_handler(filename):
    num_attributes = 0
    attributes = []
    attributes_vals = []
    labels = []
    with open(filename, 'r') as f:
        # assume the 1st column is the id, and the last column is the label
        attributes = f.readline().strip().split(',')[1:-1]
        num_attributes = len(attributes)
        for line in f.readlines():
            raw_attributes_val = line.strip().split(',')[1:]
            attributes_val = {}
            for i in range(num_attributes):
                attributes_val[attributes[i]] = raw_attributes_val[i]
            label = raw_attributes_val.pop()
            attributes_vals.append(attributes_val)
            labels.append(label)
    # assert len(attributes_vals) == len(labels)
    print(attributes, attributes_vals, labels)
    return (num_attributes, attributes, attributes_vals, labels)

class node():
    def __init__(self, value=None, next_sibiling=None, childs=None):
        self.value = value
        self.next_sibiling = next_sibiling
        self.childs = childs

class decision_tree():
    def __init__(self, num_attributes, attributes, attributes_vals, labels):
        self.num_attributes = num_attributes
        self.attributes = attributes
        self.attributes_vals = attributes_vals
        self.labels = labels

        self.counter = {}
        for label in self.labels:
            if label not in self.counter:
                self.counter[label] = 1
            else:
                self.counter[label] += 1

        self.entropy = get_entropy(self.labels)
        self.root = self.id3()

    def get_entropy(self, labels):
        count_dict = {}
        total_len = 0
        for ele in labels:
            if ele not in count_dict:
                count_dict[ele] = 1
            else:
                count_dict[ele] += 1
            total_len += 1
        rslt = 0
        for key in count_dict.keys():
            px = count_dict[key]/total_len
            rslt += (-px*log(px, 2))
        return rslt

    def id3(self):
        pass

    def _id3(self, attributes_vals, available_attributes, labels, curr_node):
        num_labels = len(labels)
        if num_labels == 1:
            curr_node.value = labels[0]
            return
        num_attributes_vals = len(attributes_vals)
        if num_attributes_vals == 0:
            return

        best_attribute = get_bestAttribute(attributes_vals, available_attributes, labels)
        for attributes_val in attributes_vals:
            vi = attributes_val[best_attribute]

    def get_bestAttribute(self, attributes_vals, available_attributes, labels):
        pass
        


if __name__ == "__main__":
    INPUT = csv_handler("playtennis.csv")
    atree= decision_tree(INPUT[0],INPUT[1], INPUT[2], INPUT[3])