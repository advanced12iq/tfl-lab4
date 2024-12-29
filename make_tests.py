import re
lines = """b/a\\2ababa
b(3)
bbaaaabbabbb
ba/ba*aaa**bab
abbaa
(bba)babaabbba
a(a)ab*babab*
aa/ab*aba
(a)
\\3bbaba/b***ba"""
lines = re.sub('/', '|', lines)
print(lines)