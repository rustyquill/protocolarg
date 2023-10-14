# database-error

player is redirected to /error.html on the finale page after the "search results have rendered"
the lambda ensures the nonce token is still valid, if not pushes the player to the index page
if still valid generates an encrypted timestamp and forwards the player to the finale page
