# Nothing  important. Just help function here

import datetime


class HelpFunc():

    def log_to_file(self, to_log):
        time_now = datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S")
        command_log = '[' + str(time_now) + ']' + " === " + to_log
        # print(command_log) #Test command_log
        f = open("C:\\Users\\p.kosowski\\PycharmProjects\\pytar-v2\\cmd_logs.txt", "a+")
        f.write('MSG >>> ' + command_log + "\n")
        print(to_log)
        return