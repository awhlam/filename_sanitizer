# Git aliases
function gp { git push $args }
function gst { git status }
function ga { git add $args }
function gcam { git add . ; if ($?) { git commit -m $args } }
function gl { git log $args }