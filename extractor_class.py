# extractor class

class Extractor(object):
	"""docstring for Extractor"""
	def __init__(self, arg):
		super(Extractor, self).__init__()
		self.arg = arg

	def iplayer_atoz_page_extractor(program_selection):
		'''arguement is soup div tag for a program.	
		Returns program title, program synopsis, no of
		episodes available, and the link to the latest episode
		'''
		# Program Title
		title = program_selection.find('p',
	            attrs={'class':
	                'list-content-item__title'}).get_text()
	    # Program Synopsis
		synopsis = program_selection.find('p',
	            attrs={'class':
	                'list-content-item__synopsis'}).get_text()
	    # Link to latest episode
		latest_episode_url = program_selection.find('a', href=True)['href']
	    # Number of episodes available
		episodes_available = program_selection.find('div',
	            attrs={'class': 'list-content-item__sublabels'}).get_text()
	    
	    
		return title, synopsis, latest_episode_url, episodes_available

	def programme_website_extractor(web_page):
		''' input  '''
		program_website_url = web_page.find('a',
		    attrs={'class': 'lnk'},
		    text='Programme website')['href']
		program_credits_url = web_page.find('a',
		    attrs={'class': 'lnk'},
		    text='Credits')

		credits_available = bool(program_credits_url)

		if credits_available:
			program_credits_url = program_credits_url['href']

		return program_website_url, program_credits_url, credits_available