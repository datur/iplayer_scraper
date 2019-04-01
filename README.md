# Iplayer Scraper v0.2

Simple Iplayer scraper using Selenium.

- The scraper iterates through each alphabetical entry in <http://bbc.co.uk/iplayer/a-z>
- This data is currently output into a json file in the current directory

Future Work

- the script is currently very slow. Given the time i would liked to have optimised the scraping to avoid duplicates and instead link programmes and episodes by id rather than having numerous repeated recommendations in similar programmes when these could just be a simple link with a programme id. 
- provide more command line options such as running a minimal version or a lookup that would check for the latest information on a show rather than having to rely on running the whole script from the start. this could be achioeved by adding a feature that takes a programme name as input looks up the programme in a mongodb store and then returns the programme id and then does a quick scrape of the programme microsite.

Improvements:

- now includes credits for each episode 
- now includes supporting content eg programme podcast information and online additional content.
- more indepth episode information and upcoming epoisodes
- more indepth recommendation information

The new json format as follows in the example from the latest results for eastenders:

    {
        programmes: [
        {
            "title": "EastEnders",
            "synopsis": "Welcome to Walford, E20.",
            "latest_episode_url": "/iplayer/episode/m0003fjy/eastenders-19032019",
            "episodes_available": "17 episodes available",
            "id": "b006m86d",
            "genre":[
                {
                    "genre":"Drama",
                    "link":"/programmes/genres/drama"
                },
                {...},
                {...}
            "format":[
                {...} #if there is format information available
            ],
            "alt-synopsis":{
                "long_synopsis":"Welcome to Walford, E20"
            },
            "supporting_content":[
                {
                    "content_title":"EastEnders: The Podcast",
                    "content_type":"promotion",
                    "content_url":"https://www.bbc.co.uk/programmes/p06sp2cr/episodes/player"
                },
                {...},
                {...}
            ],
            "recommendations":[
                {
                    "id":"b00pfnxl",
                    "title":"  Machair  \u2014 Series 5, Episode 10 ",
                    "synopsis":" 10/13 Drama G\u00e0idhlig st\u00e8idhichte ann an Le\u00f2dhas. Isle of Lewis Gaelic soap. ",
                    "link":"/programmes/b00pfnxl",
                    "long_synopsis":"Drama G\u00e0idhlig st\u00e8idhichte ann an Le\u00f2dhas. Gaelic soap based on the Isle of Lewis.",
                    "series_id":"b00vc2z8",
                    "series_name":"Series 5",
                    "days_left":"25 days left to watch",
                    "duration":"\n24 minutes\n            ",
                    "removal_date":"Mon 15 April 2019, 20:20",
                    "previous_broadcasts":[
                        {
                        "channel":"BBC ALBA",
                        "time_stamp":"2009-12-18T19:00:00+00:00",
                        "standard_date":"18 Dec 2009",
                        "time":"19:00"
                        },
                        {...},
                        {...}
                    ],
                    "broadcast":{
                        "last_on":{
                        "channel":"BBC ALBA",
                        "date_tiem":"2019-03-16T18:55:00+00:00",
                        "standard_date":"16 Mar 2019",
                        "time":"18:55"
                        }
                    },
                    "credits":null,
                    "music":null,
                    "supporting_content":[ ],
                    "genre":[
                        {
                        "genre":"Drama",
                        "link":"/programmes/genres/drama"
                        },
                        {...},
                        {...}
                    ],
                    "format":[ ],
                    "collection":null
                },
                {...},
                {...},
            ],
            "episodes": {
                "available": {
                    "episode":{
                        "id":"m0003fjy",
                        "episode_link":"https://www.bbc.co.uk/programmes/m0003fjy",
                        "episode_title":"19/03/2019",
                        "episode_synopsis":"Ruby plays with fire. Denise hatches a plan to help Patrick.",
                        "episode_time_left":"28 days left to watch (Thu 18 April 2019, 21:00)",
                        "long_synopsis":"Ruby plays with fire. Kush finds himself in a tricky situation. Denise hatches a plan to help Patrick.",
                        "days_left":"28 days left to watch",
                        "duration":"\n29 minutes\n            ",
                        "removal_date":"Thu 18 April 2019, 21:00",
                        "broadcast":{
                            "last_on":{
                                "channel":"BBC One",
                                "date_tiem":"2019-03-19T19:30:00+00:00",
                                "standard_date":"19 Mar 2019",
                                "time":"19:30"
                            },
                            "previous_broadcasts":[
                                {
                                    "channel":"BBC One",
                                    "time_stamp":"2019-03-19T19:30:00+00:00",
                                    "standard_date":"19 Mar 2019",
                                    "time":"19:30"
                                }
                            ]
                        },
                        "credits":{
                            "Bex Fowler":"Jasmine Armfield",
                            "Honey Mitchell":"Emma Barton",
                            "Jay Brown":"Jamie Borthwick",
                            "Tina Carter":"Luisa Bradshaw-White",
                            "Linda Carter":"Kellie Bright",
                            "Dot Branning":"June Brown",
                            "Martin Fowler":"James Bye",
                            "Sonia Fowler":"Natalie Cassidy",
                            "Stuart Highway":"Ricky Champ",
                            "Callum 'Halfway' Highway":"Tony Clay",
                            "Iqra Ahmed":"Priya Davdra",
                            "Sharon Mitchell":"Letitia Dean",
                            "Mick Carter":"Danny Dyer",
                            "Kim Fox-Hubbard":"Tameka Empson",
                            "Billy Mitchell":"Perry Fenwick",
                            "Rainie Branning":"Tanya Franks",
                            "Robbie Jackson":"Dean Gaffney",
                            "Kush Kazemi":"Davood Ghadami",
                            "Mitch Baker":"Roger Griffiths",
                            "Shirley Carter":"Linda Henry",
                            "Hayley Slater":"Katie Jarvis",
                            "Mariam Ahmed":"Indira Joshi",
                            "Louise Mitchell":"Tilly Keeper",
                            "Ruby Allen":"Louisa Lytton",
                            "Jack Branning":"Scott Maslen",
                            "Phil Mitchell":"Steve McFadden",
                            "Whitney Dean":"Shona McGarty",
                            "Keegan Baker":"Zack Morris",
                            "Mo Harris":"Laila Morse",
                            "Habiba Ahmed":"Rukku Nahar",
                            "Bernadette Taylor":"Clair Norris",
                            "Mel Owen":"Tamzin Outhwaite",
                            "Denise Fox":"Diane Parish",
                            "Alfie Moon":"Shane Richie",
                            "Arshad Ahmed":"Madhav Sharma",
                            "Tiffany Butcher":"Maisie Smith",
                            "Karen Taylor":"Lorraine Stanley",
                            "Kathy Beale":"Gillian Taylforth",
                            "Ted Murray":"Christopher Timothy",
                            "Stacey Fowler":"Lacey Turner",
                            "Patrick Trueman":"Rudolph Walker",
                            "Kat Moon":"Jessie Wallace",
                            "Keanu Taylor":"Danny Walters",
                            "Hunter Owen":"Charlie Winter",
                            "Max Branning":"Jake Wood",
                            "Ian Beale":"Adam Woodyatt",
                            "Jean Slater":"Gillian Wright",
                            "Amy Mitchell":"Abbie Burke",
                            "Tommy Moon":"Shay Crotty",
                            "Ricky Mitchell":"Frankie Day",
                            "Bailey Baker":"Kara-Leah Fernandes",
                            "Lily Fowler":"Aine Garvey",
                            "Janet Mitchell":"Grace",
                            "Chatham Taylor":"Alfie Jacobs",
                            "Riley Taylor":"Tom Jacobs",
                            "Dennis Rickman":"Bleu Landau",
                            "Will Mitchell":"Freddie Phillips",
                            "Writer":"Philip  Lawrence",
                            "Director":"John Dower"
                        },
                        "music":[
                            {
                                "artist":"Simon May",
                                "artist_url":"/music/artists/9e218bdf-81b7-4308-a3a8-3b147432157f",
                                "track":"\nEastenders Theme (2009 Version)\n",
                                "time_stamp":"Track plays 00:00 into Episode"
                            },
                            {
                                "artist":"Ed Sheeran",
                                "artist_url":"/music/artists/b8a7c51f-362c-4dcb-a259-bc6e0095f0a6",
                                "track":"\nCastle On The Hill\n",
                                "time_stamp":"Track plays 00:08 into Episode"
                            },
                            {
                                "artist":"Hozier",
                                "artist_url":"/music/artists/b4691384-50c3-4afd-9988-51d3ec5db65d",
                                "track":"\nFrom Eden\n",
                                "time_stamp":"Track plays 00:13 into Episode"
                            },
                            {
                                "artist":"Bob Marley & The Wailers",
                                "artist_url":"/music/artists/c296e10c-110a-4103-9e77-47bfebb7fb2e",
                                "track":"\nWaiting In Vain\n",
                                "time_stamp":"Track plays 00:23 into Episode"
                            }
                        ],
                        "supporting_content":[
                            {
                                "title":"Watch all the episodes from the last 4 weeks on BBC iPlayer",
                                "link":"https://www.bbc.co.uk/iplayer/episodes/b006m86d",
                                "summary":"Welcome to Walford, E20"
                            },
                            {
                                "title":"EastEnders: The Podcast",
                                "link":"https://www.bbc.co.uk/programmes/p06sp2cr/episodes/player",
                                "summary":"Hear exclusive off-screen stories!"
                            },
                            {
                                "title":"Have you been affected by an issue we've featured?",
                                "link":"http://www.bbc.co.uk/programmes/articles/DHjNLq6BdH5wV1p5bJ2ch9/information-and-support",
                                "summary":"Take a look at some of the organisations that can help."
                            }
                        ],
                        "genre":[
                            {
                                "genre":"Drama",
                                "link":"/programmes/genres/drama"
                            },
                            {
                                "sub_genre":"Soaps",
                                "link":"/programmes/genres/drama/soaps"
                            }
                        ],
                        "format":[

                        ],
                        "collection":null
                        }
                    },
                    {...},
                    {...}
                },
                "upcoming": [
                {
                    "channel":{
                    "name":"BBC One",
                    "link":"https://www.bbc.co.uk/bbcone"
                    },
                    "broadcast":{
                    "date":"21 Mar 2019",
                    "day":"Tomorrow",
                    "time":"19:30"
                    },
                    "id":"m0003h13",
                    "program_title":"21/03/2019",
                    "program_synopsis":"Ruby takes matters into her own hands. Kim gives Denise the encouragement she needs.",
                    "program_link":"https://www.bbc.co.uk/programmes/m0003h13",
                    "long_synopsis":"Ruby takes matters into her own hands. Whitney and Halfway think to the future. Kim gives Denise the encouragement she needs.",
                    "credits":{
                    "Bex Fowler":"Jasmine Armfield",
                    "Honey Mitchell":"Emma Barton",
                    "Jay Brown":"Jamie Borthwick",
                    "Tina Carter":"Luisa Bradshaw-White",
                    "Linda Carter":"Kellie Bright",
                    "Dot Branning":"June Brown",
                    "Martin Fowler":"James Bye",
                    "Sonia Fowler":"Natalie Cassidy",
                    "Stuart Highway":"Ricky Champ",
                    "Callum 'Halfway' Highway":"Tony Clay",
                    "Iqra Ahmed":"Priya Davdra",
                    "Sharon Mitchell":"Letitia Dean",
                    "Mick Carter":"Danny Dyer",
                    "Kim Fox-Hubbard":"Tameka Empson",
                    "Billy Mitchell":"Perry Fenwick",
                    "Rainie Branning":"Tanya Franks",
                    "Robbie Jackson":"Dean Gaffney",
                    "Kush Kazemi":"Davood Ghadami",
                    "Mitch Baker":"Roger Griffiths",
                    "Shirley Carter":"Linda Henry",
                    "Hayley Slater":"Katie Jarvis",
                    "Mariam Ahmed":"Indira Joshi",
                    "Louise Mitchell":"Tilly Keeper",
                    "Ruby Allen":"Louisa Lytton",
                    "Jack Branning":"Scott Maslen",
                    "Phil Mitchell":"Steve McFadden",
                    "Whitney Dean":"Shona McGarty",
                    "Keegan Baker":"Zack Morris",
                    "Mo Harris":"Laila Morse",
                    "Habiba Ahmed":"Rukku Nahar",
                    "Bernadette Taylor":"Clair Norris",
                    "Mel Owen":"Tamzin Outhwaite",
                    "Denise Fox":"Diane Parish",
                    "Alfie Moon":"Shane Richie",
                    "Arshad Ahmed":"Madhav Sharma",
                    "Tiffany Butcher":"Maisie Smith",
                    "Karen Taylor":"Lorraine Stanley",
                    "Kathy Beale":"Gillian Taylforth",
                    "Ted Murray":"Christopher Timothy",
                    "Stacey Fowler":"Lacey Turner",
                    "Patrick Trueman":"Rudolph Walker",
                    "Kat Moon":"Jessie Wallace",
                    "Keanu Taylor":"Danny Walters",
                    "Hunter Owen":"Charlie Winter",
                    "Max Branning":"Jake Wood",
                    "Ian Beale":"Adam Woodyatt",
                    "Jean Slater":"Gillian Wright",
                    "Amy Mitchell":"Abbie Burke",
                    "Tommy Moon":"Shay Crotty",
                    "Ricky Mitchell":"Frankie Day",
                    "Bailey Baker":"Kara-Leah Fernandes",
                    "Lily Fowler":"Aine Garvey",
                    "Janet Mitchell":"Grace",
                    "Chatham Taylor":"Alfie Jacobs",
                    "Riley Taylor":"Tom Jacobs",
                    "Dennis Rickman":"Bleu Landau",
                    "Will Mitchell":"Freddie Phillips",
                    "Writer":"Carey Andrews",
                    "Director":"John Dower"
                    },
                    "music":null,
                    "supporting_content":[
                    {
                        "title":"Watch all the episodes from the last 4 weeks on BBC iPlayer",
                        "link":"https://www.bbc.co.uk/iplayer/episodes/b006m86d",
                        "summary":"Welcome to Walford, E20"
                    },
                    {
                        "title":"EastEnders: The Podcast",
                        "link":"https://www.bbc.co.uk/programmes/p06sp2cr/episodes/player",
                        "summary":"Hear exclusive off-screen stories!"
                    },
                    {
                        "title":"Have you been affected by an issue we've featured?",
                        "link":"http://www.bbc.co.uk/programmes/articles/DHjNLq6BdH5wV1p5bJ2ch9/information-and-support",
                        "summary":"Take a look at some of the organisations that can help."
                    }
                    ],
                    "genre":[
                    {
                        "genre":"Drama",
                        "link":"/programmes/genres/drama"
                    },
                    {
                        "sub_genre":"Soaps",
                        "link":"/programmes/genres/drama/soaps"
                    }
                    ],
                    "format":[

                    ],
                    "collection":null
                },
                {...},
                {...},
                {...}   
                ]
        },
        {...},
        {...},
        {...},
        ]
    }

![Image of JSON Structure](iPlayerCataloguefinal.png)