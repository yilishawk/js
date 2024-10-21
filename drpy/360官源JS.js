var rule = {
title: '360影视[官]',
    host: 'https://www.360kan.com',
    homeUrl: 'https://api.web.360kan.com/v1/rank?cat=2&size=9',
    detailUrl: 'https://api.web.360kan.com/v1/detail?cat=fyclass&id=fyid',
    searchUrl: 'https://api.so.360kan.com/index?force_v=1&kw=**&from=&pageno=fypage&v_ap=1&tab=all',
    url: 'https://api.web.360kan.com/v1/fyfilter&size=35&pageno=fypage&callback=',
    filterable: 1,
    filter_url: 'filter/list?catid=fyclass&rank={{fl.排序}}&cat={{fl.类型}}&year={{fl.年代}}&area={{fl.地区}}',
    filter: 'H4sIAAAAAAAAA+2YS08jRxCA/4vPHGbMvrK3/IJcor1Eq4gDUqIlbLQhkVYrJINt1jYPA8vLa2MgYJtlMdhAiD1e4z8z3TP+Fxm7Xu0oGs2BQBRx81fVXV3V3VNV7XcxO/b8u3exV5NvY89jXrOjyouxsdj0xE+TJv82MfXr5HDgdCBW6eN+8nggDiA2O4bSrZLK1lCKQDov09TJNOoQeF7u2O2WaB4A6fTcqk5soQ6BbdbWVLtDNgHYZrYm6yHwvNy51z2heQA8r/JebCKwL5kd18mSLwCsmz/1ttZIB2DE5210JL4B8Lyt937WoXkA7Kdzorqb5CcA6dwv+/5ZA3UIbLO+5GfKZBOAfckf+Ye8LwCsW1lQ+QvSAbDNZE7PfySbAOJL1VtdYF+GwDbT126Hzg9h9uVACxdOlRpqyZELxxzpwi2kg/Fk/KjWL8jCbquuit1+taBb5zgCYXSEyjd0+4Y3ZAgc9GUjGEFBA/Dh3KyIDoF0/b1PokNgm9sVXTolmwCy3qa53qY5z19sig6B9+HmT9EhsG65oZwq6QAiH077yu0cGodDHOVw4lb8EcqGPw35uMjHTXlc5HFTbovcNuWWyC1Dbn/F8uCnIX8m8mem/KnIn5ryJyJ/Ysofi/yxKZd4bTNeW+K1zXhtidc247UlLtuMy5K4LDMuS+KyzLgsicuSuHTxSm9/Qs3UzPdvJyfejJy6XllXTl5OnXn01HUp4ffWvGRd7+yjtTcT069+eD0jSw2HuK3c6JCpiZnJX0ZGqfy2qnT985Qx6ufXP07PDBx7ORaL31aJ8o8TUhYQopSM0BQXUvbCykI/2VWtecoSAGxz7lol82QTIFIKXyi6ziLpADj2elUtUdlDiJL6Va6pettcvobAWbBS9s93KQsC8HqN5aBI0noAHPvuut6pUOxDMLdNnV0rp05LDmFEHdYwJNO6QBkfQQpj1b2hm4gQqZm4uyIGcFdFLKwYhRWxsOIXVqj0VkPl9tXuATc8xA9l56Hs/OfKzvitlZ1UU+UPvVqCPgtm/qJKe67jyAhh9ne17J1yKQHgbzWRlakIkrw+q2VuAAHYr7Oe38iQUwBmIk3tGYk0APZ2Y09fcbIE4HmFj+4XfikASE65dNurnFOGwL7MLakSvYQQjHzTPyRfECSHXasGrwfAulZLZ6iMIvC+NNZUqkf7AsBZtfvBn6dyiGC+ys7odYVgFBG9WZAiMgD5AC6Mlx5AlBebf/W716EYEHhes+t36WwRWLde1zkqsQj/j1dZ2AvqtBZcD9IB3EuSGeaPR7eVPwJP/ANODQBRGpdBaQ5uduXSKNXA/EXWN2Q2As/u5FW6RVMBojSFYV+WWljvF6gMIETJcHrlWBpwBNbNLXqZJukAWHfR0SnKcAjsS7ujk7Q1CDxv/0AVqQNFMNpPL8sxAMi1cKTpReCr7VyoOmU/BLaZ6gXfPdkE4AzQWw1WoQwAEOWBoRMn4icC60L+y/KKOV2gTIUQ0rjLvM8V4zEAILqyzvENBojSzntHN1JNEOQhtGg82AD+Vk+zdPTCUsP+UN2mMYKZRnzz4mtRI5Du2xeigt9Gj+ttnoz85zcikjfOktf5MPrfoCm6k3wclkv/scl/aNPvvU2XeG0z3n+3fQ9A4rXMeC2J1zLjtSReS+IdeQYg3FeBnv0LfL9z7fwYAAA=',
    filter_def: {},
    headers: {
      'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
    },
    timeout: 5000,
    class_name: '电视剧&电影&综艺&动漫',
    class_url: '2&1&3&4',
    limit: 5,
    multi: 1,
    searchable: 2,
    play_parse: true,
lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\\.m3u8|\\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else if (/NBY|youku|iqiyi|v\\.qq\\.com|pptv|sohu|le\\.com|1905\\.com|mgtv|bilibili|ixigua/.test(url)) {
            let play_Url = /bilibili/.test(url) ? 'https://www.ckplayer.vip/jiexi/?url=' : 'https://www.ckplayer.vip/jiexi/?url='; // type0的parse
            input = {
                jx: 0,
                url: url,
                playUrl: play_Url,
                parse: 1,
                header: JSON.stringify({
                    'user-agent': 'Mozilla/5.0',
                }),
            }
        } else {
            input
        }
    `,
    推荐: 'json:data;title;cover;comment;cat+ent_id;description',
    一级: 'json:data.movies;title;cover;pubdate;id;description',
    二级: 'js:\n        let html = JSON.parse(fetch(input, fetch_params));\n        let data = html.data;\n        let tilte = data.title;\n        let img = data.cdncover;\n        let vod_type = data.moviecategory.join(",");\n        let area = data.area.join(",");\n        let director = data.director.join(",");\n        let actor = data.actor.join(",");\n        let content = data.description;\n        let base_vod = {\n            vod_id: input,\n            vod_name: tilte,\n            type_name: vod_type,\n            vod_actor: actor,\n            vod_director: director,\n            vod_content: content,\n            vod_remarks: area,\n            vod_pic: urljoin2(input, img)\n        };\n        let delta = 50;\n        let vod_play = {};\n        let sites = data.playlink_sites;\n        sites.forEach(function (site) {\n            let playList = "";\n            let vodItems = [];\n            print(data)\n            if (data.allupinfo) {\n                let total = parseInt(data.allupinfo[site]);\n                print(total)\n                for (let j = 1; j < total; j += delta) {\n                    let end = Math.min(total, j + delta - 1);\n                    print(end)\n                    let url2 = buildUrl(input, { start: j, end: end, site: site });\n                    let vod_data = JSON.parse(fetch(url2), fetch_params).data;\n                    if (vod_data != null) {\n                        if (vod_data.allepidetail) {\n                            vod_data = vod_data.allepidetail[site];\n                            vod_data.forEach(function (item, index) {\n                                vodItems.push((item.playlink_num || "") + "$" + urlDeal(item.url || ""))\n                            })\n                        } else {\n                            vod_data = vod_data.defaultepisode;\n                            vod_data.forEach(function (item, index) {\n                                vodItems.push((item.period || "") + (item.name || "") + "$" + urlDeal(item.url) || "")\n                            })\n                        }\n                    }\n                }\n            } else {\n                let item = data.playlinksdetail[site];\n                vodItems.push((item.sort || "") + "$" + urlDeal(item.default_url || ""))\n            } if (vodItems.length > 0) {\n                playList = vodItems.join("#")\n            } if (playList.length < 1) {\n                return\n            } vod_play[site] = playList\n        });\n        let tabs = Object.keys(vod_play);\n        let playUrls = []; for (let id in tabs) {\n            print("id:" + id); playUrls.push(vod_play[tabs[id]])\n        } if (tabs.length > 0) {\n            let vod_play_from = tabs.join("$$$"); let vod_play_url = playUrls.join("$$$");\n            base_vod.vod_play_from = vod_play_from;\n            base_vod.vod_play_url = vod_play_url\n        }\n        VOD = base_vod;\n    ',
    搜索: 'json:data.longData.rows;titleTxt||titlealias;cover;cat_name;cat_id+en_id;description',
}
