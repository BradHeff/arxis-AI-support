from pathlib import Path
import sys

paths = str(Path(__file__).parents[0])


class Updater:
    def __init__(self, args):
        super(Updater, self).__init__()

        self.lines = []
        self.vlines = []
        self.old = ""
        self.filevers = ""
        self.prodvers = ""
        self.FileVersion = ""
        self.ProductVersion = ""

        self.new = args[1]

        self.readLines()
        self.writeLines()

    def _getPosition(self, file, text):
        nlist = [x for x in file if text in x]
        position = file.index(nlist[0])
        return position

    def readLines(self):
        with open(paths + "\\Functions.py", "r") as f:
            self.lines = f.readlines()
            pos = self._getPosition(self.lines, "Version =")
            line = self.lines[pos]
            self.old = line.split("=")[1].replace('"', "").strip()
            f.close()
        with open(paths + "\\version.rc", "r") as f:
            self.vlines = f.readlines()
            pos = self._getPosition(self.vlines, "filevers=")
            pos2 = self._getPosition(self.vlines, "prodvers=")
            pos3 = self._getPosition(self.vlines, "FileVersion'")
            pos4 = self._getPosition(self.vlines, "ProductVersion'")

            line = self.vlines[pos]
            line2 = self.vlines[pos2]
            line3 = self.vlines[pos3]
            line4 = self.vlines[pos4]

            self.filevers = line.split("=")[1].replace("(", "").replace(")", "").strip()
            self.filevers = self.filevers[0 : self.filevers.__len__() - 1]

            self.prodvers = (
                line2.split("=")[1].replace("(", "").replace(")", "").strip()
            )
            self.prodvers = self.prodvers[0 : self.prodvers.__len__() - 1]

            self.FileVersion = (
                line3.split(",")[1]
                .replace("'", "")
                .replace(")", "")
                .replace("u", "")
                .strip()
            )
            self.FileVersion = self.FileVersion[0 : self.FileVersion.__len__()]

            self.ProductVersion = (
                line4.split(",")[1]
                .replace("'", "")
                .replace(")", "")
                .replace("u", "")
                .strip()
            )
            self.ProductVersion = self.ProductVersion[0 : self.ProductVersion.__len__()]

            f.close()

    def writeLines(self):
        with open(paths + "\\Functions.py", "w") as w:
            pos = self._getPosition(self.lines, "Version =")

            self.lines[pos] = self.lines[pos].replace(
                self.old, "".join(["v", self.new])
            )

            w.writelines(self.lines)
            w.close()
        with open(paths + "\\version.rc", "w") as w:
            pos1 = self._getPosition(self.vlines, "filevers=")
            pos2 = self._getPosition(self.vlines, "prodvers=")
            pos3 = self._getPosition(self.vlines, "FileVersion'")
            pos4 = self._getPosition(self.vlines, "ProductVersion'")

            self.vlines[pos1] = self.vlines[pos1].replace(
                self.filevers, self.new.replace(".", ",")
            )
            self.vlines[pos2] = self.vlines[pos2].replace(
                self.prodvers, self.new.replace(".", ",")
            )

            self.vlines[pos3] = self.vlines[pos3].replace(self.FileVersion, self.new)
            self.vlines[pos4] = self.vlines[pos4].replace(self.ProductVersion, self.new)

            w.writelines(self.vlines)
            w.close()


if __name__ == "__main__":
    args = list(sys.argv)
    Updater(args)
