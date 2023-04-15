from bs4 import BeautifulSoup
import requests
import re
def create_link(partial_link):
	return r"""https://www.381info.com/""" + partial_link
def main():
	url = r"""https://www.381info.com/mapa-sajta.php"""
	html = requests.get(url).text
	html = str(BeautifulSoup(html, "html.parser").find(class_="tekstl"))
	html = html[248:-6]
	links = BeautifulSoup(html, "html.parser").find_all("a")
	with open("links.txt", "wt") as f:
		for l in links:
			print(create_link(l.get("href")))
			f.write(create_link(l.get("href")) + "\n")
if __name__ == "__main__":
	main()
