
ndcg_cost = zeros(length(5:5:100));
step = 100;
for i = step:step:1200
    fprintf("ON DCG of %d", i)
    ndcg_cost(i/step) = trainDCG(i);
end
