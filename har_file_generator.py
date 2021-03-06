import csv
import json
import glob
import os
from pyvirtualdisplay import Display
from pprint import pprint
import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def setup_profile(url, logdir):
	profile = webdriver.FirefoxProfile()
	profile.add_extension(extension='firebug-2.0.12.xpi')
	profile.add_extension(extension='netExport-0.9b7.xpi')
	
	profile.set_preference("browser.cache.disk.enable", False)
	domain = "extensions.firebug.";
	
	# Set default Firebug preferences
	profile.set_preference(domain + "currentVersion", "2.0.12")
	profile.set_preference(domain + "allPagesActivation", "on")
	profile.set_preference(domain + "defaultPanelName", "net")
	profile.set_preference(domain + "net.enableSites", True)
	
	# Set default NetExport preferences
	profile.set_preference(domain + "netexport.alwaysEnableAutoExport", True)
	profile.set_preference(domain + "netexport.defaultFileName", url.split("/")[-2] + "-%Y-%m-%d")
	profile.set_preference(domain + "netexport.showPreview", False)
	profile.set_preference(domain + "netexport.defaultLogDir", logdir)
	
	return profile

def start(url, logdir, iters):
	for i in range(iters):
		display = Display(visible=0, size=(800, 600))
		display.start()
		profile = setup_profile(url, logdir)
		browser = webdriver.Firefox(firefox_profile=profile)
		time.sleep(5)
		browser.get(url)
		time.sleep(8)
		browser.close()

def printAvg(logdir, outfile, iters):
	total_on_content_load = 0.0
	total_on_load = 0.0
	title = "a"
	pw_dir = os.path.dirname(os.path.realpath(__file__)) 
	files = glob.glob(logdir + "/*.har")
	log = ''
	for f in files:
		with open(f) as data_file:
			data = json.load(data_file)
			print 'Start Time: ', data["log"]["pages"][0]["startedDateTime"]
			print 'Title: ', data["log"]["pages"][0]["title"]
			title = data["log"]["pages"][0]["title"]
			print '---- Page Timings ----'
			print '\t onContentLoad', data["log"]["pages"][0]["pageTimings"]["onContentLoad"]
			print '\t onLoad: ', data["log"]["pages"][0]["pageTimings"]["onLoad"]
			log = str(data["log"]["pages"][0]["startedDateTime"]) +'\t'+ str(data["log"]["pages"][0]["title"]) +'\t'+ str(data["log"]["pages"][0]["pageTimings"]["onContentLoad"]) +'\t'+str(data["log"]["pages"][0]["pageTimings"]["onLoad"])
			total_on_content_load += float(data["log"]["pages"][0]["pageTimings"]["onContentLoad"])
			total_on_load += float(data["log"]["pages"][0]["pageTimings"]["onLoad"])

	with open(outfile, 'a+') as csvfile:
		fieldnames = ['Site', 'Iterations', 'Avg Content Load Time', 'Avg On Load Time']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writerow({'Site': title, 'Iterations': iters, 'Avg Content Load Time': float(total_on_content_load/iters), 'Avg On Load Time' : float(total_on_load/iters)})

def main():
	parser = argparse.ArgumentParser(description="Open webpages and trigger net export ")
	parser.add_argument('--url', help="url to be loaded")
	parser.add_argument('--logdir', help = ".har file log location")
	parser.add_argument('--outfile', help = "output file to write the page load times")
	parser.add_argument('--iters', help = "number of iterations to compute an avg. page load time")
	args = parser.parse_args()
	start(args.url, args.logdir, int(args.iters))
	printAvg(args.logdir, args.outfile, int(args.iters))

if __name__ == "__main__":
	main()
