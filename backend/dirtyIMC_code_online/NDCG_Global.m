

% Testing set DCG
[~,ci] = sort(Obs', 2, 'descend');
Obs_i = zeros(partsize, m);
Obs_rel = zeros(partsize, m);

for i = 1:partsize
    rel = m;
    for ii = 1:DCG_SIZE
        Obs_i(i, ci(i, ii)) = ii;
        Obs_rel(i, ci(i, ii)) = rel;
        rel = rel - 1;
    end
end

ObsDCG_R = dcg(Obs_rel,Obs_i); 

Com = X * M * Y';

[~,ci] = sort(Com, 2, 'descend');
Com_i = zeros(partsize, m);
Com_rel = zeros(partsize, m);

for i = 1:partsize
    rel = m;
    for ii = 1:DCG_SIZE
        Com_i(i, ci(i, ii)) = ii;
        Com_rel(i, ci(i, ii)) = rel;
        rel = rel - 1;
    end
end

Com_DCG_R = dcg(Com_rel, Obs_i);
NDCG_OVERALL = mean(Com_DCG_R./ObsDCG_R);

