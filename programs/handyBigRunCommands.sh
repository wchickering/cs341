## make multiple multiReRank json files from a skeleton
for param in {clicks,item_title,carts,items,queries}
do
    cat shared_multiReRank_json/k3.i0.optimal_exp.json | python programs/optimize.py coeff_$param 0 1 0.02 \
        > shared_multiReRank_json/k3.i0.0-1.coeff_${param}.json
done

## create multiReRankrc files from a template
for param in {item_title,carts,items,queries,clicks}
do
    sed 's/coeff_[^\.]\+/0-1.coeff_'$param'/' data/multiReRankrc.k3.i0.coeff.template \
        > data/multiReRankrc.k3.i0.0-1.coeff_$param
done

## fork multiple runs of multiReRank varying different parameters
for param in {clicks,item_title,carts,items,queries}
do
    export MULTIRERANK_PARAMS=data/multiReRankrc.k3.i0.0-1.coeff_$param
    programs/multiReRank.sh
done

## fork multiple recall plots
for param in {clicks,item_title,carts,items,queries}
do
    python programs/plotResults.py \
        --plot recall \
        --free-param exp_$param \
        data/000050_0.48chunk.multiReRank.k15.exp_${param}.out &
done

