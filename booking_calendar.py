from icalendar import Calendar
import datetime
import os
import requests

'''url = 'https://admin.booking.com/hotel/hoteladmin/ical.html?t=698a94e6-2d15-46c2-8ff8-1b69f4cf0ee1'
c = Calendar(requests.get(url).text)
print(c.events)
e = list(c.timeline)[0]
print(e)'''


class ApartmentCalendars:

    def __init__(self):

        self.files = []
        self.added_dates = []
        self.date_range = []
        self.apartments_status = []
        self.final_list = []

    # Spremanje datuma iz kalendara (start i end)
    def get_cal_dates(self):

        curr_dir = os.getcwd()
        os.chdir(curr_dir)
        for file in os.listdir():
            if file.endswith('.ics'):
                self.files.append(file)

        for item in self.files:
            data = open(item, 'rb')
            calendar = Calendar.from_ical(data.read())

            temp_dates = []
            for item in calendar.walk():
                if item.name == 'VEVENT':
                    temp_dates.append(item.get('dtstart').dt)
                    temp_dates.append(item.get('dtend').dt)
                    temp_dates.sort()

            data.close()
            # stvaranje listi start i end
            start_end_dates = []
            for i in range(0, len(temp_dates), 2):
                start_end_dates.append(temp_dates[i:i + 2])

            self.added_dates.append(start_end_dates)

        return self.files

    # Lista s listama datuma između starta i enda
    def adding_dates(self):
        # popunjavanje start i end listi s datumima između (zauzeto)
        for i in range(len(self.added_dates)):
            for j in range(len(self.added_dates[i])):
                start = self.added_dates[i][j][0]
                end = self.added_dates[i][j][-1]
                next_day = start + datetime.timedelta(days=1)

                while True:
                    if next_day == end:
                        break
                    else:
                        self.added_dates[i][j].extend([next_day])
                        self.added_dates[i][j].sort()
                    next_day += datetime.timedelta(days=1)
        return self.added_dates

    # definiranje datumskog raspona za prikaz u tablici na kraju
    def schedule_range(self):

        comb_lst = []
        for i in range(len(self.added_dates)):
            for j in range(len(self.added_dates[i])):
                for k in self.added_dates[i][j]:
                    comb_lst.append(k)
        next_day = min(comb_lst)
        end = max(comb_lst)

        while True:
            if next_day > end:
                break
            else:
                self.date_range.append(next_day)
            next_day += datetime.timedelta(days=1)

        return self.date_range

    # popunjavanje stupca apartmana sa statusom (ulazak. izlazak, zauzeto)
    def apartment_status(self):

        for i in range(len(self.added_dates)):
            temp = self.added_dates[i]
            ap_temp = []
            index = 0
            for i in range(len(self.date_range)):
                if index > 0:
                    if temp[index][1] == self.date_range[i] and temp[index - 1][-1] == self.date_range[i - 1]:
                        ap_temp.pop(i - 1)
                        ap_temp.insert(i, 'Izlazak/Ulazak')
                if self.date_range[i] not in temp[index]:
                    ap_temp.append('  -  ')
                elif temp[index][0] == self.date_range[i]:
                    ap_temp.append('Ulazak')
                elif temp[index][-1] == self.date_range[i]:
                    ap_temp.append('Izlazak')
                    if index < len(temp) - 1:
                        index += 1
                elif self.date_range[i] in temp[index][1:-1]:
                    ap_temp.append('Zauzeto')
            self.apartments_status.append(ap_temp)

        return self.apartments_status

    # prijedlog čišćenje se predlaže tako da ga što više bude odjednom (optimalan broj dolazaka)
    def cleaning(self):

        lst = []

        for a in range(len(self.apartments_status[0])):
            temp = []
            for b in range(len(self.apartments_status)):
                temp.append(self.apartments_status[b][a])
            lst.append(temp)
        # prva razina prioriteta
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] == 'Izlazak/Ulazak':
                    lst[i][j] = 'Izlazak/SPREMANJE/Ulazak'
        # druga razina prioriteta
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] == 'Ulazak':
                    for item in lst[i]:
                        if item == 'Izlazak/SPREMANJE/Ulazak':
                            lst[i][j] = 'SPREMANJE/Ulazak'
                if lst[i][j] == 'Izlazak':
                    for item in lst[i]:
                        if item == 'Izlazak/SPREMANJE/Ulazak':
                            lst[i][j] = 'Izlazak/SPREMANJE'
        # treća razina prioriteta
        index = 0

        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] == 'Ulazak':
                    if index == 0:
                        lst[i][j] = 'SPREMANJE/Ulazak'
                    elif index > 0:
                        for x in range(index):
                            if lst[i - 1 - x][j] == 'Izlazak/SPREMANJE':
                                break
                            elif lst[i - 1 - x][j] == 'Izlazak':
                                lst[i][j] = 'SPREMANJE/Ulazak'
                                break
                            elif i - 1 - x == 0 and lst[0][j] == '  -  ':
                                lst[i][j] = 'SPREMANJE/Ulazak'
                elif lst[i][j] == 'Izlazak':
                    start_rng = len(lst) - len(lst[i + 1:])
                    for x in range(start_rng, len(lst)):
                        if lst[x][j] != '  -  ':
                            break
                        elif x == len(lst) - 1 and lst[-1][j] == '  -  ':
                            lst[i][j] = 'Izlazak/SPREMANJE'
                    if len(lst[i][j]) == len(lst[-1][j]):
                        lst[i][j] = 'Izlazak/SPREMANJE'

            index += 1
        # četvrta razina prioriteta
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] == 'SPREMANJE/Ulazak':
                    if 'Izlazak/SPREMANJE/Ulazak' in lst[i] or 'Izlazak/SPREMANJE' in lst[i] or \
                            'SPREMANJE/Ulazak' in lst[i] and lst[i].count('SPREMANJE/Ulazak') > 1:
                        break
                    else:
                        for x in reversed(range(0, len(lst[:i]))):
                            if lst[i][j] == 'Ulazak':
                                break
                            elif lst[x][j] == '  -  ':
                                for y in range(len(lst[x])):
                                    if lst[x][y] == 'Izlazak/SPREMANJE/Ulazak' or lst[x][y] == 'Izlazak/SPREMANJE' or \
                                            lst[x][y] == 'SPREMANJE/Ulazak':
                                        lst[x][j] = 'SPREMANJE'
                                        lst[i][j] = 'Ulazak'
                                        break
                            elif lst[x][j] == 'Izlazak':
                                for y in range(len(lst[x])):
                                    if lst[x][y] == 'Izlazak/SPREMANJE/Ulazak' or lst[x][y] == 'Izlazak/SPREMANJE' or \
                                            lst[x][y] == 'SPREMANJE/Ulazak':
                                        lst[x][j] = 'Izlazak/SPREMANJE'
                                        lst[i][j] = 'Ulazak'
                                        break
                            else:
                                break
        # peta razina prioriteta
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] == 'Izlazak/SPREMANJE':
                    if 'Izlazak/SPREMANJE/Ulazak' in lst[i] or 'SPREMANJE/Ulazak' in lst[i] or \
                            'Izlazak/SPREMANJE' in lst[i] and lst[i].count('Izlazak/SPREMANJE') > 1:
                        break
                    elif 'SPREMANJE' in lst[i]:
                        for x in range(len(lst[i])):
                            if lst[i][x] == 'SPREMANJE':
                                for y in range(i + 1, len(lst)):
                                    if lst[y][x] != '  -  ':
                                        break
                                    else:
                                        for a in range(i + 1, len(lst)):
                                            if lst[i][j] == 'Izlazak':
                                                break
                                            elif lst[a][j] == '  -  ':
                                                for b in range(len(lst[a])):
                                                    if lst[a][b] == 'Izlazak/SPREMANJE/Ulazak' or lst[a][b] == 'Izlazak/SPREMANJE' or \
                                                            lst[a][b] == 'SPREMANJE/Ulazak':
                                                        lst[a][j] = 'SPREMANJE'
                                                        lst[i][j] = 'Izlazak'
                                                        lst[i][x] = '  -  '
                                                        lst[a][x] = 'SPREMANJE'
                                                        break
                                            else:
                                                break
                    else:
                        for x in range(i + 1, len(lst)):
                            if lst[i][j] == 'Izlazak':
                                break
                            elif lst[x][j] == '  -  ':
                                for y in range(len(lst[x])):
                                    if lst[x][y] == 'Izlazak/SPREMANJE/Ulazak' or lst[x][y] == 'Izlazak/SPREMANJE' or \
                                            lst[x][y] == 'SPREMANJE/Ulazak':
                                        lst[x][j] = 'SPREMANJE'
                                        lst[i][j] = 'Izlazak'
                                        break
                            elif lst[x][j] == 'Ulazak':
                                for y in range(len(lst[x])):
                                    if lst[x][y] == 'Izlazak/SPREMANJE/Ulazak' or lst[x][y] == 'Izlazak/SPREMANJE' or \
                                            lst[x][y] == 'SPREMANJE/Ulazak':
                                        lst[x][j] = 'SPREMANJE/Ulazak'
                                        lst[i][j] = 'Izlazak'
                                        break
                            else:
                                break

        self.final_list = lst
        return self.final_list


class Visual(ApartmentCalendars):

    def __init__(self):

        super().__init__()

        self.ap_list = []

    # vizualni prikaz prvog reda (datum i broj apartmana)
    def visual_first_row(self):

        ap = []
        for i in range(1, len(self.final_list[0]) + 1):
            ap.append('Apartman ' + str(i))

        ap_temp = ['Datum'.center(12, '_') + '|']
        for i in range(len(ap)):
            ap_temp.append(ap[i].center(24, '_') + '|')

        self.ap_list = ''.join(ap_temp)

    # stvaranje liste za prikaz cjelokupne sugestije spremanja
    def visual_suggestions(self):

        final_temp = []
        for i in range(len(self.date_range)):
            tmp = []
            tmp.append(str(self.date_range[i]).center(12) + '|')
            for item in self.final_list[i]:
                tmp.append(item.center(24) + '|')
            final_temp.append(''.join(tmp))

        self.final_list = final_temp

    # konačan prikaz cjelokupne sugestije spremanja apartmana
    def visual_print(self):

        print(self.ap_list)
        for item in self.final_list:
            print(item)


if __name__ == '__main__':

    while True:

        ap_cal = Visual()
        # uzimanje datuma (ulaz i izlaz) i stvaranje liste za svaki apartman
        cals = ap_cal.get_cal_dates()
        if not cals:
            print('No calendars found.')
            break
        # dodavanje datuma između ulaza i izlaza (zauzeto) za svaki apartman
        ap_cal.adding_dates()
        # stvaranje raspona svih termina svih apartmana
        ap_cal.schedule_range()
        # lista statusa popunjenosti svakog od apartmana
        ap_cal.apartment_status()
        # stvaranje sugestija spremanja apartmana
        ap_cal.cleaning()
        # stvaranje prikaza prvog reda (datum i broj apartmana)
        ap_cal.visual_first_row()
        # stvaranje liste za prikaz cjelokupnog prijedloga spremanja
        ap_cal.visual_suggestions()
        # konačni prikaz sugestije premanja svih apartmana po datumima
        ap_cal.visual_print()
        break
