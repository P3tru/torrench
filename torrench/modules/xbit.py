"""xbit.pw module."""

import requests
import logging
import sys
import time
import platform
from torrench.utilities.Config import Config


class XBit(Config):
    """
    XBit class.

    This class fetches torrents from xbit.pw,
    and diplays results in tabular form.
    Further, torrent's magnetic link
    can be printed to console.
    Torrent can be added to client directly

    This class inherits Config class. Config class inherits
    Common class. The Config class provides proxies list fetched
    from config file. The Common class consists of commonly used
    methods.

    All activities are logged and stored in a log file.
    In case of errors/unexpected output, refer logs.
    """

    def __init__(self, title):
        """Initialisations."""
        Config.__init__(self)
        self.proxies = self.get_proxies('xbit')
        self.proxy = self.proxies[0]
        self.title = title
        self.logger = logging.getLogger('log1')
        self.index = 0
        self.total_fetch_time = 0
        self.mylist = []
        self.mapper = []
        self.data = {}
        if platform.system() == "Windows":
            self.OS_WIN = True
        self.output_headers = [
                'ID', 'NAME', 'INDEX', 'SIZE', 'DISCOVERED']

    def get_data(self):
        """
        To get JSON data from xbit.pw.

        At max. 100 torrents can be fetched for given input query.
        """
        search = "api?search=%s&limit=100" % (self.title)
        start_time = time.time()
        raw = requests.get(self.proxy+search).json()
        self.total_fetch_time = time.time() - start_time
        self.data = raw

    def parse_data(self):
        """
        Parsing JSON.

        Torrent id, name, magnet, size and date are fetched.
        """
        try:
            masterlist = []
            results = self.data['dht_results']
            if results == [{}]:
                print("\nNo results found for given input!\n")
                self.logger.debug("No results fetched!")
                sys.exit(2)
            for result in results[:-1]:
                torrent_id = result['ID']
                torrent_name = result['NAME']
                # Handling Unicode characters in windows.
                if self.OS_WIN:
                    torrent_name = torrent_name.encode('ascii', 'replace').decode()
                magnet = result['MAGNET']
                torrent_size = result['SIZE']
                torrent_discovered = result['DISCOVERED']
                self.index += 1
                self.mapper.insert(self.index, (torrent_name, magnet, torrent_id))
                self.mylist = [torrent_id, torrent_name, "--"+str(self.index)+"--", torrent_size, torrent_discovered]
                masterlist.append(self.mylist)
            self.show_output(masterlist, self.output_headers)
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" % (e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)

    def after_output_text(self):
        """
        Text to be displayed after results are displayed.
        """
        try:
            print("\nTotal %d torrents" % (self.index))
            print("Total time: %.2f sec" % (self.total_fetch_time))
            self.logger.debug("fetched ALL results in %.2f sec" % (self.total_fetch_time))
            print("\nEnter torrent's index value (Maximum one index)\n")
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)

    def select_torrent(self):
        """
        To select torrent. Torrent is selected using index.

        The selected torrent's magnetic link is printed to console,
        and copied to clipboard.
        Also, torrent can be added to torrent client:
        Linux/MacOS: transmission-remote
        Windows: Default torrent client
        """
        self.logger.debug("Selecting torrent...")
        temp = 9999
        while(temp != 0):
            try:
                temp = int(input("\n\n(0=exit)\nindex > "))
                self.logger.debug("selected index %d" % (temp))
                if temp == 0:
                    print("\nBye!")
                    self.logger.debug("Torrench quit!")
                    break
                elif temp < 0:
                    print("\nBad Input!")
                    continue
                else:
                    selected_torrent, req_magnetic_link, torrent_id = self.mapper[temp-1]
                    print("Selected index [%d] - %s\n" % (temp, self.colorify("yellow", selected_torrent)))
                    self.logger.debug("selected torrent: %s ; index: %d" % (selected_torrent, temp))
                    temp2 = input("1. Print magnetic link [p]\n2. Load magnetic link to client [l]\n\nOption [p/l]: ")
                    temp2 = temp2.lower()
                    self.logger.debug("selected option: [%c]" % (temp2))
                    if temp2 == 'p':
                        self.logger.debug("printing magnetic link and upstream link")
                        print("\nMagnetic link - %s" % (self.colorify("red",  req_magnetic_link)))
                        self.copy_magnet(req_magnetic_link)
                    elif temp2 == 'l':
                        try:
                            self.logger.debug("Loading magnetic link to client")
                            self.load_torrent(req_magnetic_link)
                        except Exception as e:
                            self.logger.exception(e)
                            continue
            except (ValueError, IndexError, TypeError) as e:
                print("\nBad Input!")
                self.logger.exception(e)
                continue


def main(title):
    """Execution begins here."""
    try:
        print("\n[XBit.pw]\n")
        xb = XBit(title)
        print("Using %s" %(xb.colorify("yellow", xb.proxy)))
        print("Fetching results...")
        xb.get_data()
        xb.parse_data()
        xb.after_output_text()
        xb.select_torrent()
    except KeyboardInterrupt:
        xb.logger.debug("Keyboard interupt! Exiting!")
        print("\n\nAborted!")


if __name__ == "__main__":
    print("It's a module!")
