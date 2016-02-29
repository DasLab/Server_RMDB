
from src.models import *


def parse_history():
    hist_list = []
    hist = HistoryItem.objects.all()
    for h in hist:
        lines = h.content
        lines = [line for line in lines.split('\r\n') if line.strip()]
        ls_1_flag = 0
        ls_2_flag = 0
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip()
            if lines[i][0] == "#":
                lines[i] = "<span class=\"lead\"><b>" + lines[i][1:] + "</b></span><br/>"
            elif lines[i][0] != '-':
                if lines[i][0] == "!":
                    lines[i] = "by <kbd><i>" + lines[i][1:] + "</i></kbd><br/><br/>"
                else:
                    lines[i] = "<p>" + lines[i] + "</p><p><ul>"

            else:
                if lines[i][:2] != '-\\':
                    lines[i] = "<li><u>" + lines[i][1:] + "</u></li>"
                    if ls_1_flag:
                        lines[i] = "</ul></p>" + lines[i]
                    ls_1_flag = i

                else:
                    lines[i] = "<li>" + lines[i][2:] + "</li>"
                    if ls_2_flag < ls_1_flag:
                        lines[i] = "<ul><p>" + lines[i]
                    ls_2_flag = i        
        lines.append("</ul></ul><br/><hr/>")
        date_string = h.date.strftime("%b %d, %Y (%a)")
        lines.insert(0, "<i>%s</i><br/>" % date_string)
        hist_list.insert(0, ''.join(lines))

        return hist_list

