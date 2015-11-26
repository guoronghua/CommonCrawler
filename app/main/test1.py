#coding=utf-8
def f_to_json(obj,result):
    u"""
    递归函数调用
    """
    if type(obj) == types.DictType:
        result.append("{")
        is_null = True
        for k,v in obj.items():
            is_null = False
            result.append("'%s':"%k)
            f_to_json(v,result)
            result.append(",")
        if not is_null:
            result.pop()
        result.append("}")
    elif type(obj) == types.ListType:
        result.append("[")
        is_null = True
        for elem in obj:
            is_null = False
            f_to_json(elem,result)
            result.append(",")

        if not is_null:
            result.pop()

        result.append("]")
    elif type(obj) == types.IntType:
        result.append("%s"%obj)
    elif type(obj) == types.StringType:
        result.append("'%s'"%obj)

    return "".join(result)

def stack_to_json(obj):
    result = []
    stack = []
    stack.append(obj)
    while stack:
        elem = stack.pop()
        if type(elem) == types.DictType:
            stack.append("{")
            is_null = True
            for k,v in elem.items():
                is_null = False
                stack.append("'%s'"%k)
                stack.append(":")
                if type(v) == types.StringType:
                    stack.append("'%s'"%v)
                else:
                    stack.append(v)
                stack.append(",")
            if not is_null:
                stack.pop()
            stack.append("}")
        elif type(elem) == types.ListType:
            stack.append("[")
            is_null = True
            for e in elem:
                is_null = False
                if type(e) == types.StringType:
                    stack.append("'%s'"%e)
                else:
                    stack.append(e)
                stack.append(",")

            if not is_null:
                stack.pop()
            stack.append("]")

        elif type(elem) in( types.IntType,types.StringType):
            result.append("%s"%elem)

        else:
            print 'other',elem
            break
    result.reverse()
    return "".join(result)


if __name__ == "__main__":
    r = []
    d = {"a":[{"c":"v","g":"gg"}],"a2":["a","b","c",{"k":"v"}]}

    print 'original dict====',d
    print 'function to json ====',f_to_json(d,r)

    print 'stack to json========',stack_to_json(d)