## make multiple multiReRank json files from a skeleton
#for param in {item_title,carts,items,queries}
#do
#    cat data/k3.start.json | python programs/optimize.py exp_$param 0.01 \
#        > data/exp_${param}.json
#done

## create multiReRankrc files from a template
#for param in {item_title,carts,items,queries}
#do
#    sed 's/exp_[^\.]\+/exp_'$param'/' data/multiReRankrc.exp_clicks \
#        > data/multiReRankrc.exp_$param
#done

## fork multiple runs of multiReRank varying different parameters
#for param in {clicks,item_title,carts,items,queries}
#do
#    export MULTIRERANK_PARAMS=data/multiReRankrc.exp_$param
#    programs/multiReRank.sh &
#done

## fork multiple recall plots
#for param in {clicks,item_title,carts,items,queries}
#do
#    python programs/plotResults.py \
#        --plot recall \
#        --free-param exp_$param \
#        data/000050_0.48chunk.multiReRank_exp_${param}.out
#done

