from math import log

SAMPLE_FILE_NAME = "waiting.csv"

def csv_handler(filename):
    # csv to recognizable data type
    num_attributes = 0
    num_labels = 0
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
            num_labels += 1
    return (attributes, attributes_vals, labels, num_attributes, num_labels)

def get_splited_input(FROM_INPUTS, with_attribute, of_value):
    # A helper function is used to split 
    # the input regarding to their attributes 
    # and attributes' values into the standard format
    old_attributes = FROM_INPUTS[0]
    old_attributes_vals = FROM_INPUTS[1]
    old_labels = FROM_INPUTS[2]

    new_attributes = [x for x in old_attributes if x != with_attribute]
    new_num_attributes = FROM_INPUTS[3] - 1
    new_attributes_vals = []
    new_labels = []
    new_num_labels = 0

    counter = 0
    for bundle in old_attributes_vals:
        if bundle[with_attribute] == of_value:
            new_attributes_vals.append(bundle)
            new_labels.append(old_labels[counter])
            new_num_labels += 1

        counter += 1
    return (new_attributes, new_attributes_vals, new_labels, new_num_attributes, new_num_labels)

def get_entropy(INPUTS):
    labels = INPUTS[2]
    count_dict = {}
    total_len = INPUTS[4]
    for ele in labels:
        if ele not in count_dict:
            count_dict[ele] = 1
        else:
            count_dict[ele] += 1
    rslt = 0
    for key in count_dict.keys():
        px = count_dict[key]/total_len
        rslt += (-px*log(px, 2))
    return rslt

def get_best_attribute(INPUTS):
    attributes = INPUTS[0]
    attributes_vals = INPUTS[1]
    num_labels = INPUTS[4]
    curr_entropy = get_entropy(INPUTS)

    curr_max_info_gain = -1
    rslt = None
    for attribute in attributes:
        # get unique possible values
        possible_attributes_vals = [x[attribute] for x in attributes_vals]
        possible_attributes_vals = list(set(possible_attributes_vals))
        
        # max infogain computation
        this_attributes_entropy = 0
        for possible_val in possible_attributes_vals:
            splited_input = get_splited_input(INPUTS, attribute, possible_val)
            p = splited_input[4]/num_labels
            entropy_here = p * get_entropy(splited_input)
            this_attributes_entropy += entropy_here
        info_gain = curr_entropy - this_attributes_entropy
        if info_gain > curr_max_info_gain:
            curr_max_info_gain = info_gain
            rslt = (attribute, possible_attributes_vals)
    return rslt

def get_tree(INPUTS):
    max_gain_next_attribute = get_best_attribute(INPUTS)
    labels = INPUTS[2]
    if labels.count(labels[0]) == INPUTS[-1]:
        return labels[0]
    if max_gain_next_attribute == None:
        return None # If we reach here, it means the sample is not sufficient to generalize a modal
    max_gain_next_attribute, possible_attributes_vals = max_gain_next_attribute
    rslt_tree = {max_gain_next_attribute:{}}
    for possible_attributes_val in possible_attributes_vals:
        splited_input = get_splited_input(INPUTS, max_gain_next_attribute, possible_attributes_val)
        rslt_tree[max_gain_next_attribute][possible_attributes_val] = get_tree(splited_input)
    return rslt_tree

if __name__ == "__main__":
    INPUT = csv_handler(SAMPLE_FILE_NAME)
    modal = get_tree(INPUT)
    print(modal)
    '''
    With this sample, the modal would look like:
    {'Pat': {
        'SOME': 'T', 
        'NONE': 'F', 
        'FULL': {
            'Price': {
                '$$$': 'F', 
                '$': {
                    'Est': {
                        '10~30': 'T', 
                        '>60': 'F', 
                        '30~60': {
                            'Bar': {
                                'T': 'T', 
                                'F': 'F'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    '''
    # Using pydot we can easily visulize the tree
    # Credits 
    # https://stackoverflow.com/questions/13688410/dictionary-object-to-decision-tree-in-pydot
    '''
    import pydot
    def draw(parent_name, child_name):
        edge = pydot.Edge(parent_name, child_name)
        graph.add_edge(edge)

    def visit(node, parent=None):
        for k,v in node.items():
            if isinstance(v, dict):
                # We start with the root node whose parent is None
                # we don't want to graph the None node
                if parent:
                    draw(parent, k)
                visit(v, k)
            else:
                draw(parent, k)
                # drawing the label using a distinct name
                draw(k, v)

    graph = pydot.Dot(graph_type='graph')
    visit(modal)
    graph.write_png('example1_graph.png')
    '''


