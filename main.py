from parser import Grammar

def main():
    grammar = Grammar()
    grammar.readGrammar()
    grammar.prepareForGeneration()
    grammar.test()

if __name__ == "__main__":
    main()