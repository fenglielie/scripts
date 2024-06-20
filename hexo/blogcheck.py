import os
import sys

# 是否接受代码块的缩进
allow_code_indent = False

error_count = 0

def is_list(line):
    s1 = line.startswith("* ") or line.startswith("- ") or line.startswith("+ ")
    s2 = (line == "*\n") or (line == "-\n") or (line == "+\n")

    return s1 or s2


def is_sublist(line):
    return is_list(line.lstrip())


def is_quote(line):
    return line.startswith("> ") or (line == ">\n")


def is_subquote(line):
    return is_quote(line.lstrip())


def is_orderlist(line):
    return line.split(". ", 1)[0].isdigit()


def is_ordersublist(line):
    return is_orderlist(line.lstrip())


def is_latex(line):
    return line.startswith("$$")


def is_sublatex(line):
    return is_latex(line.lstrip())


def is_sublatex_strict(line):
    return (not is_latex(line)) and is_sublatex(line)


def is_code(line):
    return line.startswith("```")


def is_subcode(line):
    return is_code(line.lstrip())


def is_subcode_strict(line):
    return (not is_code(line)) and is_subcode(line)


def check_format(lines):
    errors = []

    previous_line = ""
    line_number = 1

    in_code_block = False  # 用于跟踪是否在代码块中
    in_latex_block = False  # 用于跟踪是否在公式块中
    code_previous_line = ""  # 用于确保缩进一致
    latex_previous_line = ""  # 用于确保缩进一致

    for line in lines:
        # 处于代码块边界时，检查代码块的缩进整齐
        if is_subcode(line):
            in_code_block = not in_code_block

            if in_code_block:  # 如果正在进入代码块
                code_previous_line = line

            else:  # 如果正在退出代码块
                indent_in = code_previous_line.split("```", 1)[0]
                indent_out = line.split("```", 1)[0]

                # 要求缩进一致
                if indent_in != indent_out:
                    errors.append(
                        (line_number - 1, code_previous_line, line, "code error")
                    )

                # 只在退出时检查两个边界的缩进，因此一个代码块只会检查一次
                if (not allow_code_indent) and (len(indent_in) + len(indent_out) > 0):
                    errors.append(
                        (line_number - 1, code_previous_line, line, "code indent error")
                    )

                # 不允许代码块的退出边界的前一行是空行
                if not previous_line.strip():
                    errors.append(
                        (
                            line_number - 1,
                            previous_line,
                            line,
                            "code boundary empty line error",
                        )
                    )

        # 处于公式块边界时，检查公式块的缩进整齐
        if is_sublatex(line):
            in_latex_block = not in_latex_block

            if in_latex_block:  # 如果正在进入公式块
                latex_previous_line = line
            else:  # 如果正在退出公式块
                indent_in = latex_previous_line.split("$$", 1)[0]
                indent_out = line.split("$$", 1)[0]

                # 要求缩进一致
                if indent_in != indent_out:
                    errors.append(
                        (line_number, latex_previous_line, line, "latex error")
                    )

        ## 如果当前不位于代码块或者公式块边界或内部，则会继续检查
        if (not in_code_block) and (not in_latex_block):
            # 检查当前行是否是列表，并且要求前一行非空
            if (is_list(line) or is_orderlist(line)) and previous_line.lstrip():
                # 合法情况
                flag = (
                    is_sublist(previous_line)
                    or is_ordersublist(previous_line)
                    or is_subcode(previous_line)
                    or is_sublatex(previous_line)
                )

                if not flag:
                    errors.append((line_number, previous_line, line, "list error"))

            # 检查当前行是否是引用，并且要求前一行非空
            if (is_quote(line) or is_subquote(line)) and previous_line.lstrip():
                # 合法情况
                flag = is_subquote(previous_line)

                if not flag:
                    errors.append((line_number, previous_line, line, "quote error"))

        previous_line = line
        line_number += 1
    return errors


def main():
    global error_count
    error_count = 0
    show_error = True
    root_dir = "source/_posts"
    for root, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".md"):
                continue

            md = os.path.join(root, file)
            # print("Checking file:", md)
            lines = []
            with open(md, "r", encoding="utf-8", newline="") as f:
                lines = f.readlines()
            errors = check_format(lines)
            if errors:
                if not show_error:
                    print(f"- {len(errors)} errors in {md}")
                for error in errors:
                    if show_error:
                        print(f"[error {error_count+1}]:")
                        print(f"[{error[3]}] at {md}:{error[0]}: \n{error[1]}{error[2]}")
                    error_count += 1
            if error_count > 10 and show_error:
                print("Too many errors...")
                show_error = False


if __name__ == "__main__":
    main()

    if error_count == 0:
        print("blogcheck: pass")

    sys.exit(error_count)
