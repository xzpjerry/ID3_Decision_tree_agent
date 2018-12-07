from collections import Counter
from math import log

# SAMPLE_FILE_NAME = "waiting.csv"
# SAMPLE_FILE_NAME = "golf.csv"
SAMPLE_FILE_NAME = "home_inSF.csv"


class STD_INPUT:
    def __init__(self, labels, attributes, data, curr_best_attri=None, curr_best_threshold=None):
        self.labels = labels
        self.attributes = attributes
        self.data = data
        self.curr_best_threshold = curr_best_attri
        self.curr_best_threshold = curr_best_threshold
        # attrs = vars(self)
        # print(', '.join("%s: %s" % item for item in attrs.items()))


class Utility_func:
    @staticmethod
    def get_entropy(data):
        rslt = 0
        labels = [x["label"] for x in data]
        count_dict = Counter(labels)
        num_labels = len(labels)
        for _, val in count_dict.items():
            px = val / num_labels
            rslt += (-px * log(px, 2))
        return rslt

    @staticmethod
    def get_info_gain(whole_data, sub_datas):
        rslt = Utility_func.get_entropy(whole_data)
        num_whole_rec = len(whole_data)
        for sub in sub_datas:
            px = len(sub) / num_whole_rec
            rslt -= (px * Utility_func.get_entropy(sub))
        return rslt


class C45:

    def __init__(self, filename):
        self.continuous_labels = ['<', '>']
        init_INPUT = self.load(filename)
        self.root = self.get_tree(init_INPUT)
        # print(self.root)

    def load(self, filename):
        # csv to recognizable data type
        num_attributes = 0
        num_labels = 0
        raw = []
        attributes = []
        num_attributes = 0
        labels = set()
        with open(filename, 'r') as f:
            # assume the 1st column is the id, and the last column is the label
            attributes = f.readline().strip().split(',')[1:-1]
            num_attributes = len(attributes)
            for line in f.readlines():
                raw_attributes_val = line.strip().split(',')[1:]
                attributes_val = {}

                for i in range(num_attributes):
                    attributes_val[attributes[i]] = raw_attributes_val[i]
                    if "(continuous)" in attributes[i]:
                        attributes_val[attributes[i]] = float(
                            attributes_val[attributes[i]])
                attributes_val["label"] = raw_attributes_val[-1]
                label = raw_attributes_val.pop()
                raw.append(attributes_val.copy())
                labels.add(label)
                num_labels += 1
        labels = list(labels)
        return STD_INPUT(labels, attributes, raw)

    def is_pure(self, INPUT):
        first_label = INPUT.data[0]["label"]
        for rec in INPUT.data:
            if rec["label"] != first_label:
                return False
        return first_label

    def get_most_common_label(self, INPUT):
        count_dict = Counter(INPUT.labels)
        for key in count_dict:
            count_dict[key] = 0
        for rec in INPUT.data:
            count_dict[rec["label"]] += 1
        return count_dict.most_common(1)[0][0]

    def get_best_splicer(self, INPUT):
        subset = []
        max_info_ratio = None
        best_threshold = None
        best_attri = None
        attribute_available_vals = None
        for attri in INPUT.attributes:
            possible_vals = [x[attri] for x in INPUT.data]
            num_vals = len(possible_vals)
            if "(continuous)" in attri:
                possible_vals = sorted(possible_vals)
                for i in range(num_vals - 1):
                    thisv = possible_vals[i]
                    nextv = possible_vals[i + 1]
                    if thisv != nextv:
                        possible_thresh = (thisv + nextv) / 2
                        less_set = []
                        greater_set = []
                        for rec in INPUT.data:
                            if rec[attri] > possible_thresh:
                                greater_set.append(rec)
                            else:
                                less_set.append(rec)
                        new_info = Utility_func.get_info_gain(
                            INPUT.data, [less_set, greater_set])
                        p_less = (len(less_set) / num_vals)
                        p_great = (len(greater_set) / num_vals)
                        split_info = (-p_less * log(p_less, 2)) - \
                            (p_great * log(p_great, 2))
                        newinfo_ratio = new_info / split_info if split_info != 0 else new_info
                        if max_info_ratio == None or newinfo_ratio > max_info_ratio:
                            subset = [less_set, greater_set]
                            max_info_ratio = newinfo_ratio
                            best_threshold = possible_thresh
                            best_attri = attri
                            attribute_available_vals = None
            else:
                possible_vals_counter = Counter(possible_vals)
                possible_vals = set(possible_vals)
                map(lambda x: [x], possible_vals)
                possible_vals = list(possible_vals)
                possible_subs = [[] for i in possible_vals]
                counter = 0
                for val in possible_vals:
                    for rec in INPUT.data:
                        if rec[attri] == val:
                            possible_subs[counter].append(rec)
                    counter += 1

                new_info = Utility_func.get_info_gain(
                    INPUT.data, possible_subs)
                split_info = 0
                for _, val in possible_vals_counter.items():
                    px = val / num_vals
                    split_info += (-px * log(px, 2))
                newinfo_ratio = new_info / split_info if split_info != 0 else new_info
                if max_info_ratio == None or newinfo_ratio > max_info_ratio:
                    subset = possible_subs
                    max_info_ratio = newinfo_ratio
                    best_threshold = None
                    best_attri = attri
                    attribute_available_vals = possible_vals
        # print((best_attri, best_threshold, max_info_ratio))
        return (best_attri, best_threshold, subset, attribute_available_vals)

    def get_tree(self, INPUT):
        if len(INPUT.data) < 1:
            return "Maybe_fail"
        possible_final_label = self.is_pure(INPUT)
        if possible_final_label != False:
            # print(INPUT.attributes, possible_final_label)
            return possible_final_label
        if len(INPUT.attributes) < 1:
            return self.get_most_common_label(INPUT)
        best_attri, its_thresh, subsets, attribute_available_vals = self.get_best_splicer(
            INPUT)
        available_attributes = INPUT.attributes.copy()
        available_attributes.remove(best_attri)
        this_node = {}
        is_continuous = its_thresh != None
        node_name = ("" if not is_continuous else str(its_thresh)) + best_attri
        this_node[node_name] = {}
        counter = 0
        for sub in subsets:
            new_INPUT = STD_INPUT(INPUT.labels, available_attributes, sub)
            if is_continuous:
                this_node[node_name][self.continuous_labels[counter]
                                     ] = self.get_tree(new_INPUT)
            else:
                this_node[node_name][attribute_available_vals[counter]
                                     ] = self.get_tree(new_INPUT)
            counter += 1
        return this_node


if __name__ == "__main__":
    modal = C45(SAMPLE_FILE_NAME).root
    import pprint
    pprint.pprint(modal)
    
    # import pydot
    # def draw(parent_name, child_name):
    #     edge = pydot.Edge(parent_name, child_name)
    #     graph.add_edge(edge)

    # def visit(node, parent=None, depth=0):
    #     for k,v in node.items():
    #         if parent:
    #             draw(parent, k+"@depth"+str(depth))
    #         if isinstance(v, dict):
    #             # We start with the root node whose parent is None
    #             # we don't want to graph the None node
    #             visit(v, k+"@depth"+str(depth), depth+1)
    #         else:
    #             # drawing the label using a distinct name
    #             draw(k+"@depth"+str(depth), v+"@depth"+str(depth))
    # graph = pydot.Dot(graph_type='graph')
    # visit(modal)
    # graph.write_png('example1_graph.png')




