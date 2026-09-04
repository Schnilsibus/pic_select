from .pic_select import start
from .test import test_code

# TODO: make resizable
# TODO: add window in which nothing will be loaded i.e.: -6 | -3 | current | 3 | 6 loaded till +/-6 but only once image +/-4 is reached will 3 new pictures be (un)loaded
# TODO: PROBLEM: reqesting new image during initial load seems to make the app stuck
# TODO: PROBLEM: sometimes code gets "stuck": rapid clicks will cause that you can only click from one to another load frame while the loader is executing a lot of consecutive BACK - FOR - BACK - FOR requests 


def main():
    start()

if __name__ == "__main__":
    main()