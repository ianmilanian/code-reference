// While on a Twitter press 'F12' then in the Console run the following code.

function toNum(s) {
	let n = s.split("K");
	return n.length > 1 ? Number(n[0]) * 1000 : Number(n[0]);
}

var reflections = [];
var tweets = document.querySelectorAll("div.tweet");
for (let i=0; i < tweets.length; ++i) {
    let tweet = tweets[i];
    if (tweet.hasAttribute("data-retweet-id"))
        continue;
	let d = tweet.getAttribute("data-tweet-id");
    let r = tweet.querySelector("div.ProfileTweet-action.ProfileTweet-action--reply    > button > span > span");
    let s = tweet.querySelector("div.ProfileTweet-action.ProfileTweet-action--retweet  > button > span > span");
    let f = tweet.querySelector("div.ProfileTweet-action.ProfileTweet-action--favorite > button > span > span");
    reflections.push({
		"tweet-id":  d ? toNum(d)             : 0,
		"retweets":  r ? toNum(r.textContent) : 0,
		"shares":    s ? toNum(s.textContent) : 0,
		"favorites": f ? toNum(f.textContent) : 0
	});
};

var sumRows = {"tweet-id":"total", "retweets":0, "shares":0, "favorites":0};
reflections.forEach(function(row) {
	sumRows["retweets"]  += row["retweets"];
	sumRows["shares"]    += row["shares"];
	sumRows["favorites"] += row["favorites"];
});
reflections.push(sumRows);
console.table(reflections);
