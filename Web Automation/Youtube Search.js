// Expand Channel Results
var searchString = "guardians";
window.scrollTo(0, document.body.scrollHeight);
$$('ytd-grid-video-renderer').forEach(function(n) {
    if (!n.querySelector('#video-title').title.toLowerCase().includes(searchString)) {
        n.remove();
    };
});
