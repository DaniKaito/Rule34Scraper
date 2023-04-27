import requests
from bs4 import BeautifulSoup
import os
from random import randint
from time import sleep
import json

META_CLASSNAMES = ["tag-type-copyright tag", "tag-type-character tag", "tag-type-artist tag", "tag-type-general tag", "tag-type-metadata tag"]

cookies = {"gdpr":"1"}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

DOMAIN: str = "https://rule34.xxx/"
SCRAPED_FILEPATH: str = ".\\scraped.txt"

def main():
	scrapedImages = getScraped()
	outputPath = createOutPath()
	scrapeUrl = input("\nInsert image gallery url to scrape: ")
	imgPages = getImgs(scrapeUrl, scrapedImages)
	for imgUrl in imgPages:
		if imgUrl not in scrapedImages:
			downloadImg(outputPath, imgUrl)
			with open(SCRAPED_FILEPATH, "a") as f:
				f.write(imgUrl)
				f.write("\n")
			sleep(randint(1, 5))
		else:
			print(f"Already scraped: {imgUrl}")

def downloadImg(outputPath, imgUrl):
	try:
		print(f"\n\nNow analyzing the following url: {imgUrl}")
		r = requests.get(imgUrl, cookies=cookies, headers=headers)
		soup = BeautifulSoup(r.text, "html.parser")
		imgUrl =soup.find("img", {"id":"image"})["src"]
		imgContent = requests.get(imgUrl, cookies=cookies, headers=headers).content
		ul = soup.find("ul", {"id":"tag-sidebar"})
		copyright = getMeta(ul, META_CLASSNAMES[0])
		characters = getMeta(ul, META_CLASSNAMES[1])
		artist = getMeta(ul, META_CLASSNAMES[2])
		general = getMeta(ul, META_CLASSNAMES[3])
		meta = getMeta(ul, META_CLASSNAMES[4])
		imgName = "_".join(["-".join(artist), "-".join(characters)])
		if len(imgName) > 240:
			imgName = imgName[:240]
		print(f"image name is: {imgName}")
		imgOutputPath = getOutputPath(outputPath, imgName)
		infoOutputPath = imgOutputPath + ".json"
		imgOutputPath = imgOutputPath + ".png"
		with open(imgOutputPath, "wb") as f:
			f.write(imgContent)
			print(f"Successfully downloaded the image")
			print(f"image path: {imgOutputPath}")
		imgInfo = {"copyright":copyright, "characters":characters, "artist":artist, "general":general, "meta":meta}
		with open(infoOutputPath, "w") as f:
			json.dump(imgInfo, f, ensure_ascii=False, indent=1)
			print(f"Info dumped: {infoOutputPath}")
	except:
		pass	


def getOutputPath(out, img):
	counter = 1
	while True:	
		imgName = "_".join([img, str(counter)])
		outPath = os.path.join(out, imgName)
		if not os.path.exists(outPath + ".png"):
			return outPath
		counter += 1

def getMeta(list, className):
	metaList = []
	for listItem in list.find_all("li", {"class":className}):
		metaTag = listItem.find("a").find_next().get_text()
		metaList.append(metaTag)
	return metaList

def getImgs(url, scraped):
	imgArr = []
	counter = 1
	while True:
		try:
			print(f"Now analyzing page number {counter}")
			r = requests.get(url, cookies=cookies, headers=headers)
			soup = BeautifulSoup(r.text, "html.parser")
			for img in soup.find("div", {"class":"content"}).find_all("span", {"class":"thumb"}):
				imgUrl = img.find("a")["href"]
				imgUrl = "/".join([DOMAIN, imgUrl])
				if imgUrl not in scraped:
					imgArr.append(imgUrl)
			counter += 1
			url ="/".join([DOMAIN, soup.find("div", {"class":"pagination"}).find("a", {"alt":"next"})["href"]])
			sleep(randint(1, 3))
		except Exception as e:
			break
	print(f"Found a total of {len(imgArr)} images from the gallery")
	return imgArr


def getScraped():
	if not os.path.exists(SCRAPED_FILEPATH):
		with open(SCRAPED_FILEPATH, "w"):
			print(f"Scraped urls not found; txt file created")
			return []
	scrapedImages = open(SCRAPED_FILEPATH, "r").readlines()
	scrapedImages = [line.replace("\n", "") for line in scrapedImages]
	print(f"Found a total of {len(scrapedImages)} scraped images")
	return scrapedImages

def createOutPath():
	outPath = input("Insert image output path: ")
	if not os.path.exists(outPath):
		os.mkdir(outPath)
		print(f"output path successfully created")
	return outPath

if __name__ == "__main__":
	main()