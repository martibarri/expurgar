import argparse


def input_choice(msg):
    choice = input(f"{msg}").lower()
    while choice not in ["y", "n", ""]:
        print('please input "y/n"')
        choice = input(f"{msg}").lower()
    return choice


class Expurgar:
    def __init__(self, filename, chain):
        self.filename = filename
        self.chain_id = 0
        self.file_length = None
        self.chain = chain
        self.results = []

    def build_chain(self, byte: bytes, count: int, start: int):
        chain = {
            "chain_id": self.chain_id,
            "byte": byte,
            "chain_start": start,
            "chain_count": count,
        }
        self.chain_id += 1
        print(chain)
        self.results.append(chain)

    def file_analyzer(self):
        f = open(self.filename, "rb", newline=None)
        last_byte = b""
        count = 1
        while byte := f.read(1):
            if byte == last_byte:
                count += 1
            else:
                if count > self.chain:
                    # save chain
                    self.build_chain(last_byte, count, (f.tell() - 1) - count)
                # start over
                count = 1
            last_byte = byte
        if count > self.chain:
            # save last chain
            self.build_chain(last_byte, count, f.tell() - count)
        self.file_length = f.tell()
        print(f"Total file bytes: {self.file_length}")
        f.close()

    def remove_chain(self, remove_id: int):
        if remove_id >= 0 and (remove_id <= self.chain_id):
            try:
                chain_to_remove = list(
                    filter(lambda x: x.get("chain_id") == remove_id, self.results)
                )[0]
            except IndexError:
                print("chain not found")
            else:
                print("chain to remove:")
                print(chain_to_remove)
                chain_start = chain_to_remove.get("chain_start")
                chain_count = chain_to_remove.get("chain_count")
                # read file
                f = open(self.filename, "rb", newline=None)
                first_part = f.read(chain_start)
                f.seek(chain_count + chain_start)
                second_part = f.read(self.file_length)  # rest of the file
                f.close()
                # save file
                new_filename = self.filename + ".stripped"
                f = open(new_filename, "wb", newline=None)
                f.write(first_part)
                f.write(second_part)
                f.close()
                print(f"file {new_filename} saved")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, type=str)
    parser.add_argument("-c", "--chain", default=80, type=int)
    args = parser.parse_args()
    expurgar = Expurgar(args.file, args.chain)
    expurgar.file_analyzer()
    save_choice = input_choice("remove chain? [y/N] ")
    if save_choice == "y":
        try:
            remove_id = int(input("Enter id: "))
        except ValueError:
            print("Invalid id")
        else:
            expurgar.remove_chain(remove_id)


if __name__ == "__main__":
    main()
