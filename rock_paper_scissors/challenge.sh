#!/usr/bin/env bash

goal app method \
    --app-id "40" \
    --method "create_challenge(string)void" \
    -f "ALF62RMQWIAT6JO2U4M6N2XWJYM7T2XB5KFWP3K6LXH6KUG73EXFXEABAU" \
    --app-account "MH5IDGBKUC2GB6OJ6WKFW6KQA7E55MHBKEYJMZ64OYTI5VJXNMCEWEGHGM" \
    --arg '"Hghiu7bni3kdii731k3io8="' \
    -o challenge-call.tx

goal clerk send \
    -a "100000" \
    -t "UGXES2XHGCB4SR6VYO4G4SWOQU4JXC4T6X6XUFHNGGSO7EGIIZ5QYQA4RY" \
    -f "ALF62RMQWIAT6JO2U4M6N2XWJYM7T2XB5KFWP3K6LXH6KUG73EXFXEABAU" \
    -o challenge-wager.tx

cat challenge-call.tx challenge-wager.tx > challenge-combined.tx
goal clerk group -i challenge-combined.tx -o challenge-grouped.tx
goal clerk split -i challenge-grouped.tx -o challenge-split.tx

goal clerk sign -i challenge-split-0.tx -o challenge-signed-0.tx
goal clerk sign -i challenge-split-1.tx -o challenge-signed-1.tx

cat challenge-signed-0.tx challenge-signed-1.tx > challenge-signed-final.tx

goal clerk rawsend -f challenge-signed-final.tx