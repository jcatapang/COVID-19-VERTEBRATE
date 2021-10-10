from selenium import webdriver
import pandas as pd
import time
import json

urls = pd.read_csv('3-1-21_9-9-21.csv', header=None)[0].to_list()
options = webdriver.ChromeOptions() 
options.add_argument("user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data")
driver = webdriver.Chrome(executable_path='C:/Users/Admin/Documents/chromedriver_win32/chromedriver.exe', options=options)

for url in urls:
	post_id = url.split("story_fbid=")[1]
	url = url+"&id=156566631021264"
	print(url)
	react_url = "https://m.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier="+post_id
	comment_dict = dict()
	comment_dict["url"] = url

	driver.get(react_url)
	indiv_reacts = driver.find_elements_by_class_name("_5p-9")
	comment_dict["reactions"] = dict()
	for react in indiv_reacts:
		stats = react.get_attribute("aria-label")
		number = stats.split(" ")[0]
		if "K" in number:
			number = int(float(number.split("K")[0])*1000)
		else:
			number = int(number)

		if "to this post" in stats:
			comment_dict["reactions"]["total"] = number
		elif "Like" in stats:
			comment_dict["reactions"]["likes"] = number
		elif "Haha" in stats:
			comment_dict["reactions"]["laughs"] = number
		elif "Love" in stats:
			comment_dict["reactions"]["loves"] = number
		elif "Angry" in stats:
			comment_dict["reactions"]["angries"] = number
		elif "Care" in stats:
			comment_dict["reactions"]["cares"] = number
		elif "Sad" in stats:
			comment_dict["reactions"]["sads"] = number
		elif "Wow" in stats:
			comment_dict["reactions"]["wows"] = number
	comment_dict["comments"] = dict()

	if len(indiv_reacts) != 0:
		driver.get(url)
	else:
		break
	more_comments = True
	counter = 1
	comment_count = 1

	while more_comments == True:
		try:
			more = driver.find_elements_by_class_name("_108_")
			for m in more:
				if 'story_fbid='+post_id in m.get_attribute('href'):
					if counter != 10:
						m.click()
						counter += 1
						time.sleep(0.5)
					else:
						more_comments = False
		except:
			time.sleep(0.5)
			try:
				more = driver.find_elements_by_class_name("_108_")
				for m in more:
					if 'story_fbid='+post_id in m.get_attribute('href'):
						if counter != 10:
							m.click()
							counter += 1
							time.sleep(0.5)
						else:
							more_comments = False
			except:
				more_comments = False

	comments = driver.find_elements_by_class_name("_2b06")
	for idx, comment in enumerate(comments):
		if idx < 100:
			name = comment.text.split('\n')[0]
			text = comment.text.split('\n')[1]
			comment_dict["comments"]["comment_"+str(comment_count)] = dict()
			comment_dict["comments"]["comment_"+str(comment_count)]['name'] = name
			comment_dict["comments"]["comment_"+str(comment_count)]['raw_text'] = text
			comment_count += 1
		else:
			break

	comment_count = 1
	reacts = driver.find_elements_by_class_name("_14v8")
	for idx, react in enumerate(reacts):
		if idx < 100:
			try:
				comment_dict["comments"]["comment_"+str(comment_count)]['reaction_count'] = int(react.text)
			except:
				try:
					comment_dict["comments"]["comment_"+str(comment_count)]['reaction_count'] = 0
				except:
					pass
			comment_count += 1
		else:
			break

	with open('data/'+post_id+'.json', 'w') as f:
		json.dump(comment_dict, f)
driver.close()