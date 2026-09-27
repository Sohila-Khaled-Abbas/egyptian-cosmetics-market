import os
import re

tmdl_dir = r"powerbi\Cleopatra_Cosmetics_Report.SemanticModel\definition"

def check_m_block(name, code):
    parens = 0
    curlies = 0
    squares = 0
    in_string = False
    in_block_comment = False
    lines = code.splitlines()
    for line_idx, line in enumerate(lines, 1):
        i = 0
        while i < len(line):
            ch = line[i]
            if not in_string and not in_block_comment and line[i:i+2] == '//':
                break
            if not in_string and not in_block_comment and line[i:i+2] == '/*':
                in_block_comment = True
                i += 2
                continue
            if in_block_comment and line[i:i+2] == '*/':
                in_block_comment = False
                i += 2
                continue
            if in_block_comment:
                i += 1
                continue
            if ch == '"':
                if in_string and i + 1 < len(line) and line[i+1] == '"':
                    i += 2
                    continue
                in_string = not in_string
                i += 1
                continue
            if not in_string:
                if ch == '(': parens += 1
                elif ch == ')': parens -= 1
                elif ch == '{': curlies += 1
                elif ch == '}': curlies -= 1
                elif ch == '[': squares += 1
                elif ch == ']': squares -= 1
                if parens < 0:
                    print(f"ERROR: Extra closing paren in {name} at line {line_idx}: {line}")
                    return False
                if curlies < 0:
                    print(f"ERROR: Extra closing curly in {name} at line {line_idx}: {line}")
                    return False
                if squares < 0:
                    print(f"ERROR: Extra closing square bracket in {name} at line {line_idx}: {line}")
                    return False
            i += 1
    if parens != 0 or curlies != 0 or squares != 0 or in_string or in_block_comment:
        print(f"ERROR: Mismatch in {name}: parens={parens}, curlies={curlies}, squares={squares}, in_string={in_string}, in_block_comment={in_block_comment}")
        return False
    return True

expr_file = os.path.join(tmdl_dir, "expressions.tmdl")
with open(expr_file, "r", encoding="utf-8") as f:
    content = f.read()

blocks = re.findall(r"expression\s+([a-zA-Z0-9_]+)\s*=\s*```(.*?)```", content, re.DOTALL)
print(f"Found {len(blocks)} multiline expressions in expressions.tmdl")
all_ok = True
for name, body in blocks:
    if not check_m_block(f"expr:{name}", body):
        all_ok = False

single_exprs = re.findall(r"expression\s+([a-zA-Z0-9_]+)\s*=\s*([^\r\n`]+)", content)
print(f"Found {len(single_exprs)} single-line expressions in expressions.tmdl")
for name, body in single_exprs:
    # Only check if it looks like an M expression
    if not check_m_block(f"expr_single:{name}", body):
        all_ok = False

tables_dir = os.path.join(tmdl_dir, "tables")
for tf in os.listdir(tables_dir):
    if not tf.endswith(".tmdl"): continue
    with open(os.path.join(tables_dir, tf), "r", encoding="utf-8") as f:
        t_content = f.read()
    parts = re.findall(r"partition\s+[^\r\n=]+=\s*m\s*\r?\n\s*mode:\s*import\s*\r?\n\s*source\s*=\s*```(.*?)```", t_content, re.DOTALL)
    for p in parts:
        if not check_m_block(f"table:{tf}", p):
            all_ok = False

if all_ok:
    print("SUCCESS: All M expressions in expressions.tmdl and tables/*.tmdl have perfectly balanced syntax!")
else:
    print("FAILURE: Syntax errors detected.")
