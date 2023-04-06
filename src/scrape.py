import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

def getdata(url):
    # add header to prevent being blocked (403 error) by wordpress websites
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    return r.text


def get_links(website_link, website):
    html_data = getdata(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    list_links = []
    for link in soup.find_all("a", href=True):
        # Append to list if new link contains original link
        if str(link["href"]).startswith((str(website))):
            list_links.append(link["href"])

        # Include all href that do not start with website link but with "/"
        if str(link["href"]).startswith("/"):
            if link["href"] not in dict_href_links:
                print(link["href"])
                dict_href_links[link["href"]] = None
                link_with_www = website + "/"+ link["href"][1:]
                print("adjusted link =", link_with_www)
                list_links.append(link_with_www)

    # Convert list of links to dictionary and define keys as the links and the values as "Not-checked"
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links


def get_subpage_links(l, website):
    for link in tqdm(l):
        # If not crawled through this page start crawling and get links
        if l[link] == "Not-checked":
            dict_links_subpages = get_links(link, website)
            # Change the dictionary value of the link to "Checked"
            l[link] = "Checked"
        else:
            # Create an empty dictionary in case every link is checked
            dict_links_subpages = {}
        # Add new dictionary to old dictionary
        l = {**dict_links_subpages, **l}
    return l

def get_subpages(link):
    # add websuite WITH slash on end
    website = link
    # create dictionary of website
    dict_links = {website:"Not-checked"}

    counter, counter2 = None, 0
    while counter != 0:
        counter2 += 1
        dict_links2 = get_subpage_links(dict_links, website)
        
        counter = sum(value == "Not-checked" for value in dict_links2.values())

        print("")
        print("THIS IS LOOP ITERATION NUMBER", counter2)
        print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
        print("NUMBER OF 'Not-checked' LINKS = ", counter)
        print("")
        dict_links = dict_links2
        # Save list in json file
        a_file = open("fuqua_duke_edu.json", "w")
        json.dump(dict_links, a_file)
        a_file.close()


if __name__ == "__main__":
    dict_href_links = {}
    get_subpages("https://pratt.duke.edu")