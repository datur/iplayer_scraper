# Todo

    [ ] scrape episode/all to gather gather better series information
    [ ] use imdbpy to get progam id and other information
    [ ] rotten tomatoes coming out this week
    [ ] argparse

## todo from 20/02

    [ ] convert json to rdf
    [ ] scrape rotten tomatoes
    [ ] get imdb id
        [ ] criteria if it was on bbc and credits match maybe
        [ ] if cannot locate
        [ ] go through the credits entities and search for a credit [ ] matching show name
    [ ] get credits people imdb id
    [ ] complete
    [/] tvdb search function
    [ ] scrape bbc by series
    [ ] fix ccbc entries
    [ ] brand -> series -> episode
    [ ] programme website get genre format
    [ ] go through each episode page
    [ ] film profile - check out the tags for episodes as not currently working - film nght too
    [ ] for past episodes get broadcast info last on ttag
    [ ] change time left to available untill date
    [ ] air date air time
    [ ] iplayer alphabet suffix -> programmes for that suffix -> programme website extraction(synopsis, genre etc) -> episodes -> all -> season by season episode extraction -> episode page -> credits, episode synopsis, recommendations

    major restructure is required as current structure does not make sense

    full extract structure as follows:
        = loop a through z -> This works currently
            = loop through each program on current alphabet entry -> this works currently
            = get latest episode url / get program general info ie name, and short synopsis -> currently works
            = visit latest episode site to access program website -> currently works
                = if program website unavailable then get info from curr page -> ongoing
            = from program website get - long synopsis, airing information, recommendations, genre, format
            = visit episode section if available
            = go through and get all available episodes and follow link for longer synopsis and credits and genre format
            - go through upcoming episodes if available
            - go through all tab for more indepth series information
            - get music played on episode


## Testing TODO

Shows to test

    bbc one show:   https://www.bbc.co.uk/programmes/b0bxbvtl
                    https://www.bbc.co.uk/programmes/b006m86d

    one off show:   https://www.bbc.co.uk/programmes/p00sydsh
                    https://www.bbc.co.uk/programmes/b0645530

    cbbc and cbbies:https://www.bbc.co.uk/cbbc/shows/all-over-the-place

    film:           https://www.bbc.co.uk/programmes/b05nbsc4
                    https://www.bbc.co.uk/iplayer/episode/p06zb13p/it-follows
