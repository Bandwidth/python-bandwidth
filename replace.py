import re
def convert_comment_string_to_snake_case(s):
  """
  Changes String to from camelCase to snake_case
  :param s: String to convert
  :rtype: String
  :rertuns: String converted to snake_case
  """
  # regex = r"(\s+##\s+\'\w+)((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))(\w+\'.+)"
  # a = re.compile("(\s+##\s+\'\w+)((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))(\w+\')")
  regex = r"(\s+##\s+\"\w+)((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))(\w+\".+)"
  #a = re.compile("(\s+##\s+\'\w+)((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))(\w+\')")
  # m.group(1)sub(r'_\1', s).lower()

  result = re.match(regex, s)
  if result:
    return result.group(1) + "_" + result.group(2).lower() + result.group(3) + '\n'
  else:
    return s

with open('bandwidth/catapult/__init__.py') as f:
    with open('out2.py', 'w') as e:
      for line in f:
        e.write(convert_comment_string_to_snake_case(line))
