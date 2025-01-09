from parser import Grammar, AST

def main():
    grammar = Grammar()
    grammar.readGrammar()
    grammar.prepareForParsing()
    regex_list = [
        "(a|(?2)b)(a\\1)",
        "(a|(?2)b)(a(?1))",
        "(a|(?2))(a|(bb(\\1)))(a)",
        "(a|(?2))(a|(bb\\4))(a)",
        "(a)*(\\1)*",
        "(a(?2)b|c)((?1)(\\1))",
        "((a(?1)b|c)|(a|b))((?3)(\\2))",
        "(\\1)(a|b)",
        "(?1)(a|b)",
        "(a(?1)a|b)",
        "((?1)a|b)",
        "(a|b)*\\1",
        "(?1)(a|b)*(?1)",
        "(aa|bb)(?1)",
        "(aa|bb)\\1",
        "(a|(bb))(a|\\2)",
        "(a|(bb))(a|(?3))",
        "(a|(?2))(a|(bb\\1))",
        "(a(?1)b|c)",
        "(a(?1)a)"
    ]
    for word in regex_list:
        ast = AST(word, grammar)

    # grammar.test()
    # regexp = Regexp(input())
    # regexp.getCaptureGroups()
    # for key, value in regexp.captureGroups.items():
    #     print(f"{key} : {regexp.regexp[value[0] : value[1]+1]}")
    # for item in regexp.expLinks:
    #     print(regexp.regexp[item[0] : item[1] + 1])

if __name__ == "__main__":
    main()