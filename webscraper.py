from bs4 import BeautifulSoup
import requests
from timeit import default_timer as timer
from csv import writer

# NOTE: DONT RUN THIS CODE THE DATA ALREADY BEEN COLLECTED!
# the url of the website
# The first page of the website
#  https://www.sahibinden.com/kiralik
# The second page of the website and the rest of pages can be aquired by just increasing the number by 20
# https://www.sahibinden.com/kiralik?pagingOffset=20


# to see how long the program took
start = timer()
# this will hold the data of the houses
data = []
# columns of the csv file
header = ["fiyat", "city", "district", "neighborhood"]


# this function will go into the list item link and aquire the house info
def find_HouseInfo(url, index, item_price, city, district, neighborhood):
    # print("I am inside the find_houseinfo function")
    # print(url)
    response = requests.get("https://www.emlakjet.com" + url)
    info_row = [None] * 55
    soup = BeautifulSoup(response.text, 'html.parser')
    house_price = soup.find_all('div', class_='_2TxNQv')
    try:
        price = house_price[0].text
    except:
        print("error")
        print(house_price)
        print(index)
        print(url)
        if (house_price != []):
            price = house_price.text
        else:
            print("error with no property")
            print(house_price)
            price = item_price

    index_of = price.find("L")
    price = price[:index_of + 1]
    info_row[0] = price
    info_row[1] = city
    info_row[2] = district
    info_row[3] = neighborhood

    # this will aquire all the house info in the page
    house_info = soup.find_all('div', class_='_35T4WV')
    if (house_info == []):
        print("no house info")
    # this will aquire the house info that are related to the house inside each div that is inside the main div
    for info in house_info:
        if info.find_all('div', class_='_1bVOdb'):
            if (info.find_all('div', class_='_1bVOdb')[0].text in header):
                pass
            else:
                header.append(info.find_all('div', class_='_1bVOdb')[0].text)
            try:
                info_row[header.index(info.find_all('div', class_='_1bVOdb')[
                    0].text)] = info.find_all('div', class_='_1bVOdb')[1].text
            except:
                continue
        else:
            pass
    data.append(info_row)


def print_data():
    # NOTE: IT HAS BEEN EDITED SO IT WOULDNT CHANGE THE ACTUAL DATA FILE
    # this will write the data in a csv file
    with open('_.csv', 'w', encoding="utf-8-sig", newline='') as csv_file:
        csv_writer = writer(csv_file)
        csv_writer.writerow(header)
        for i in range(0, len(data)):
            csv_writer.writerow(data[i])


# this function will aquire the links of the houses in each page


def aquire_HouseLinks():
    current_offeset = 0
    # print("the links of the houses are: ")
    cities = ["Adana", "adiyaman", "afyonkarahisar", "agri", "amasya", "Ankara", "Antalya", "Artvin", "aydin", "balikesir", "Bilecik", "bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "canakkale", "cankiri", "corum", "Denizli", "diyarbakir", "Edirne", "elazig", "Erzincan", "Erzurum", "eskisehir", "Gaziantep", "Giresun", "gumushane", "Hatay", "Isparta", "mersin", "istanbul", "izmir", "Kars", "Kastamonu", "Kayseri", "kirklareli", "kirsehir", "Kocaeli", "Konya", "kutahya", "Malatya", "Manisa", "kahramanmaras", "Mardin", "mugla", "mus", "nevsehir", "nigde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "tekirdag", "Tokat", "Trabzon",  "sanliurfa", "usak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman", "kirikkale", "Batman", "sirnak", "bartin", "Yalova", "karabuk", "Kilis", "Osmaniye", "duzce"
              ]

    ending_index = 0
    for city in cities:
        url = f"https://www.emlakjet.com/kiralik-konut/{city.lower()}"
        # this will aquire the last page index
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        last_page_index = soup.find_all('div', class_='_3au2n_')
        if (last_page_index == []):
            ending_index = 0
        else:
            ending_index = int(last_page_index[-2].text)
            print(city)
            print(ending_index)

        for i in range(ending_index):
            url = ""
            if (i == 0):
                url = f"https://www.emlakjet.com/kiralik-konut/{city.lower()}"
            else:
                url = f"https://www.emlakjet.com/kiralik-konut/{city.lower()}/{i+1}/"

            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            list_items = soup.find_all('div', class_='_3qUI9q')
            if (list_items != []):
                # this will aquire the links that are related to the house
                for list_item in list_items:
                    if list_item.find('a', class_='_3qUI9q'):
                        link = list_item.find('a', class_='_3qUI9q')
                        price = list_item.find('p', class_='_2C5UCT')
                        location = list_item.find(
                            'div', class_='_2wVG12').text.split(" - ")
                        city_name = location[0]
                        district = location[1]
                        neighborhood = location[2]
                        find_HouseInfo(link.get('href'), i,
                                       price.text, city_name, district, neighborhood)

                    else:
                        pass


if __name__ == "__main__":

    aquire_HouseLinks()
    elapsed_time = timer() - start  # in seconds
    print(
        f'the program took {elapsed_time} to aquire house links and write data inside the array')

    elapsed_time = timer() - start  # in seconds
    print_data()
    print(f'the program took {elapsed_time} to print the data')
