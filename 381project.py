#!/usr/bin/env python3
import requests
import re
import os.path
import threading 
import curses
from threading import Thread
from threading import Lock
from bs4 import BeautifulSoup
from time import sleep
out_lock = Lock()
q_lock = Lock()
done_lock = Lock()
found_lock = Lock()
failed_lock= Lock()
status_lock = Lock()
empty_lock = Lock()
total_len= 4119
def create_link(partial_link):
	return r"""https://www.381info.com/""" + partial_link
def load_queue():
	global q, done
	file_name = "links.txt"

	if os.path.isfile(file_name):
		with open(file_name, "rt") as f:
			q = f.readlines()
			q = [i.strip("\n") for i in q]
	else:
		print(file_name + " doesn't exist")
		return False
	return True
		
def screen():
	global input_break, q, done, stdscr, thread_num, found, thread_status, empty
	curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

	stdscr.refresh()
	q_progress=str(total_len-len(q)) + " out of " + str(total_len) + "\r"
	done_progress="Done: " + str(len(done))
	threads_alive="Alive : " + str(threading.active_count()-1) + " ||  " + str(thread_num)
	stdscr.addstr(0, 0, q_progress)
	stdscr.addstr(1, 0, "Done: " + str(len(done)))
	stdscr.addstr(1, 15, "Found: " + str(found))
	stdscr.addstr(1, 30, "Empty: " + str(empty))
	stdscr.addstr(2, 0, "Failed: " + str(failed))
	stdscr.addstr(4, 0, threads_alive)
	cols=3
	i=0
	
	while i < len(threads):
		j=0
		while j < cols and i < len(threads):
			t_name=threads[i].name + ": " 
			if(threads[i].is_alive()):
				if(thread_status[threads[i].name] == "S"):
					t_alive="S"
					color=curses.color_pair(3)

				else:
					t_alive="T"
					color=curses.color_pair(1)
			else:
				t_alive="N"
				color=curses.color_pair(2)
			stdscr.addstr(6+int(i/cols), 20*j, t_name)
			stdscr.addstr(6+int(i/cols), 20*j+len(t_name), t_alive, color)
			i+=1
			j+=1

def save():
	global q, done, empty, failed
	with open("done.txt", "wt") as f:
		for i in done:
			f.write(i + "\n")
	with open("info.txt", "wt") as f:
		f.write("Ukupno: " + str(found) + "\n")
		f.write("Prazne: " + str(empty) + "\n")
		f.write("Sa Brojem: " + str(found-empty) + "\n")
		f.write("Greske: " + str(failed) + "\n")
		

def get_item(link):
	global q, done, out_f, thread_status
	while True:
		try:
			req = requests.get(link)
		except:
			sleep(1)
			continue
		soup = BeautifulSoup(req.text, "html.parser")
		soup = soup.find(class_="paketa")
		if soup is None:
			return False

		with status_lock:
			thread_status[threading.current_thread().name] = "#"
		name = soup.find(itemprop="name").text
		city = soup.find(itemprop="locality").text
		phones = re.findall(r"""\d{3}[/][0-9-]+""", soup.text)
		if phones:
			with out_lock:
				out_f.write(str(name) +"\n"+ str(city) +"\n" + str( phones) +  "\n"+link+"\n\n")
			return True
		return False

def find_items(link):
	global q, done, failed, found, empty
	out=""
	try:
		req = requests.get(link)
	except:
		with q_lock:
			q.append(link)
		with failed_lock:
			failed+=1
		return out
	soup=BeautifulSoup(req.text, "html.parser")
	items=soup.find_all(class_="firme-item")		
	if items:
		for i in items:
			item_link=create_link((i.find("a").get("href")))
			key = re.search(r"""[a-z, -]*$""", item_link).group()
			if key not in done:
				with done_lock:
					done.add(key)
				with found_lock:
					found+=1
				if not get_item(item_link):
					with empty_lock:
						empty+=1
	stranice=soup.find(class_="stranice")
	if stranice:
		new_link=stranice.find("a")
		if new_link:
			out=create_link(new_link.get("href"))
	return out
		
	
		
						

def thread():
	global q, input_break, thread_status
	while q and not input_break:
		with q_lock:
			link=q.pop()
		res=find_items(link)
		if res:
			find_items(res)


	

def main():
	global q, done, input_break, stdscr, thread_num, threads, failed, out_f, found, thread_status, empty
	input_break = False
	empty = 0 
	q = list()
	done = set()
	found = 0
	threads = list()
	thread_status = dict()
	out_f = open("result.txt", "wt", encoding="utf-8")
	failed=0
	found=0
	if not load_queue():
		return
	thread_num = int(input("Number of Threads: \n"))
	for i in range(1, thread_num+1):
		t=Thread(target=thread, name="Thread " + str(i), daemon=True)
		thread_status[t.name] = "#"
		print("Thread "+str(i)+" Starting ...")
		t.start()
		threads.append(t)
	#input_t=Thread(target=input_thread, name="Input Thread", daemon=True)
	#print("Input Thread Starting ...")
	#input_t.start()
	sleep(1)
	stdscr=curses.initscr()
	curses.start_color()
	curses.init_color(0, 0, 0, 0)

	while threading.active_count()>1:
		screen()
		sleep(1)
	sleep(5)
	curses.endwin()
	out_f.close()
	save()
	if input_break:
		print("Stopped")
	else:
		print("DONE")
	
	

if __name__ == "__main__":
	main()
