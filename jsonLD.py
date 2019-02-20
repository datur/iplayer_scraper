import json
from pyld import jsonld
'''
Relevant Classes
Brand				 	eg show name
	Broadcast 			broadcast event associated with a service and a particular version of an episode
	Broadcaster 		organisation incharge of broadcast
	Category 			provides a way of classifying programs
	episode 			a particular episode
	Format				anchorpoint for formats similar to genre
	genre				the genre of the episode or series
	Person				a person
	Place				a location
	Programme 			Brand, Series Or Episode
	Season				a group of broadcasts
	series 				a brand and its season
	service 			contains information on the broadcast

'''

context = {
    "@context": {
        "brand": "http://purl.org/ontology/po/Brand",
        "actor": "http://purl.org/ontology/po/actor",
        "anchor": "http://purl.org/ontology/po/anchor",
        "author": "http://purl.org/ontology/po/author",
        "broadcast": "http://purl.org/ontology/po/broadcast",
        "broadcast_on": "http://purl.org/ontology/po/broadcast_on",
        "broadcaster": "http://purl.org/ontology/po/broadcaster",
        "commentator": "http://purl.org/ontology/po/commentator",
        "credit": "http://purl.org/ontology/po/credit",
        "director": "http://purl.org/ontology/po/director",
        "duration": "http://purl.org/ontology/po/duration",
        "episode": "http://purl.org/ontology/po/episode",
        "executive producer": "http://purl.org/ontology/po/executive_producer",
        "format": "http://purl.org/ontology/po/format",
        "long synopsis": "http://purl.org/ontology/po/long_synopsis",
        "medium synopsis": "http://purl.org/ontology/po/medium_synopsis",
        "microsite": "http://purl.org/ontology/po/microsite",
        "news reader": "http://purl.org/ontology/po/news_reader",
        "parent Series": "http://purl.org/ontology/po/parent_series",
        "parent service": "http://purl.org/ontology/po/parent_service",
        "participant ": "http://purl.org/ontology/po/participant",
        "performer": "http://purl.org/ontology/po/performer",
        "Person": "http://purl.org/ontology/po/person",
        "position": "http://purl.org/ontology/po/position",
        "producer": "http://purl.org/ontology/po/producer",
        "schedule date": "http://purl.org/ontology/po/schedule_date",
        "Series": "http://purl.org/ontology/po/series",
        "service": "http://purl.org/ontology/po/service",
        "short synopsis": "http://purl.org/ontology/po/short_synopsis",
        "time": "http://purl.org/ontology/po/time"
    }
}
