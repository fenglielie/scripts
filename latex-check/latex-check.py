import os
import sys
import argparse

error_count = 0

punctuations = (
    " ",
    "-",
    "_",
    ".",
    ",",
    "!",
    "?",
    ":",
    ";",
    "(",
    ")",
    "。",
    "，",
    "！",
    "？",
    "：",
    "；",
    "（",
    "）",
    "{",
    "}",
)


def check_dollar_sign_spacing(file_path):
    global error_count
    errors = []

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line_number, line in enumerate(lines, start=1):
        dollar_indices = [i for i, char in enumerate(line) if char == "$"]

        for idx in range(len(dollar_indices)):
            cur_idx = dollar_indices[idx]
            is_even_idx = idx % 2 == 0

            # Check rules based on the index of the dollar sign
            if is_even_idx:  # Even index (left dollar sign)
                if cur_idx > 0:  # Not the first character
                    if line[cur_idx - 1] not in punctuations:
                        errors.append(
                            (
                                cur_idx,
                                line_number,
                                line,
                                "Missing space before '$'",
                            )
                        )
            else:  # Odd index (right dollar sign)
                if (
                    cur_idx < len(line) - 1 and line[cur_idx + 1] != "\n"
                ):  # Not the last character
                    if line[cur_idx + 1] not in punctuations:
                        errors.append(
                            (
                                cur_idx,
                                line_number,
                                line,
                                "Missing space after '$'",
                            )
                        )

    return errors[::-1]


def fix_dollar_sign_spacing(file_path, lines, errors):
    modified_lines = lines.copy()  # 复制原始行以便后续修改

    for line_number, line in enumerate(lines):
        for error in errors:
            if error[1] == line_number + 1:  # 对应的行
                cur_idx = error[0]
                is_even_idx = "before" in error[3]

                # 根据索引进行修改
                if is_even_idx:  # Even index (left dollar sign)
                    modified_lines[line_number] = (
                        modified_lines[line_number][:cur_idx]
                        + " "
                        + modified_lines[line_number][cur_idx:]
                    )
                else:  # Odd index (right dollar sign)
                    modified_lines[line_number] = (
                        modified_lines[line_number][: cur_idx + 1]
                        + " "
                        + modified_lines[line_number][cur_idx + 1 :]
                    )

    # 交互式确认更新
    confirm = input(f"Confirm changes for {file_path}? (y/n): ")
    if confirm.lower() == "y":
        with open(file_path, "w", encoding="utf-8", newline="\n") as file:
            file.writelines(modified_lines)
        print(f"Changes saved for {file_path}.")


def main():
    global error_count
    error_count = 0

    parser = argparse.ArgumentParser(description="Check LaTeX dollar sign spacing.")
    parser.add_argument(
        "--fix", action="store_true", help="Interactively fix spacing issues"
    )
    args = parser.parse_args()

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".tex"):
                tex_file_path = os.path.join(root, file)
                print(f"Checking spacing for: {tex_file_path}")
                errors = check_dollar_sign_spacing(tex_file_path)

                if errors:
                    for error in errors:
                        print(
                            f"[error {error_count + 1}]: "
                            f"{error[3]} at {tex_file_path}:{error[1]} ({error[0]})"
                        )
                        error_count += 1

                    if args.fix:
                        fix_dollar_sign_spacing(
                            tex_file_path,
                            open(tex_file_path, "r", encoding="utf-8").readlines(),
                            errors,
                        )

    if error_count == 0:
        print("latex-check: pass")

    sys.exit(error_count)


if __name__ == "__main__":
    main()
