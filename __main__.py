from .pic_select import start

# TODO: [add comand line args]
# TODO: add fullscreen possibility
# TODO: [make safe functionality]
# TODO: [possible to open directory instead of file]
# TODO: make resizable
# TODO: add window i which nothing will be loaded i.e.: -6 | -3 | current | 3 | 6 loaded till +/-6 but only once image +/-4 is reached will 3 new pictures be (un)loaded
# TODO: reqesting new image during initial load seems to make the app stuck

def main():
    start()

if __name__ == "__main__":
    main()