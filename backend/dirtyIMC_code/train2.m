
function [M, XR, YR] = train2()
 
TmpX = full(mmread("sparseXactor.mm.mtx"));
TmpY = full(mmread("sparseYactor.mm.mtx"));

[j,k] = size(TmpX);
[s,t] = size(TmpY);

%%%%%% Orthogonal-triangular decomposition %%
%optX/optY is the good feature space
dim = k;
[X, XR] = qr(TmpX,0);
Xorth = X(:,dim+1:end);
optX = X(:,1:dim);
[Y, ~] = qr(TmpY,0);
Yorth = Y(:, dim+1:end);
optY = Y(:,1:dim);

% Perturb feature X and Y
feature_perturb = 0.2;
replace_dim = ceil(feature_perturb*k);
X = optX;
%X(:,1:replace_dim) = Xorth(:,1:replace_dim);
Y = optY;
%Y(:,1:replace_dim) = Yorth(:, 1:replace_dim);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Obs = mmread("sparseN.mm.mtx");
[m,n] = size(Obs);

% X = TmpX;
% Y = TmpY;
% [j,k] = size(X);
%PCA on x matrix to rank 12
% if (strcmp(feature, "genre"))
%      X = pcasolver(X, 12, j);
% end


obsf = Obs';
perm = randperm(n);
ObsShuf = obsf(perm,:);
XShuf = X(perm,:);

start = 1;
folds=10;
if (mod(n, folds))
    return %THIS WOULD NEED a change in size of folds
end
partsize = n/folds;

lambda = logspace(-5,5,100);
%lambda = [100];
%lambda = [10^-3 10^-2 10^-1 10^0 10^1 10^2];
%lambda = [.9030];

lambda1 = [100000000];
lambda_loss = zeros(folds,length(lambda));
lambda_ratio = zeros(folds,length(lambda));

%Completed = zeros(34,1188);

for part = start:folds
    if part == start
        ObsFoldTrain = ObsShuf(start*partsize+1:folds*partsize,:);
        XFoldTrain = XShuf(start*partsize+1:folds*partsize,:);
        ObsFoldTest = ObsShuf(start:start*partsize,:);
        XFoldTest = XShuf(start:start*partsize,:);
    elseif part == folds
        ObsFoldTrain = ObsShuf(start:(folds-1)*partsize, :);
        XFoldTrain = XShuf(start:(folds-1)*partsize, :);
        ObsFoldTest = ObsShuf((folds-1)*partsize+1:folds*partsize,:);
        XFoldTest = XShuf((folds-1)*partsize+1:folds*partsize,:);
    else
        ObsFoldTrain = vertcat(ObsShuf(start:(part-1)*partsize, :), ...
            ObsShuf((part*partsize)+1:folds*partsize,:));
        XFoldTrain = vertcat(XShuf(start:(part-1)*partsize, :), ...
            XShuf((part*partsize)+1:folds*partsize,:));
        
        ObsFoldTest = ObsShuf((part-1)*partsize+1:(part)*partsize, :);
        XFoldTest = XShuf((part-1)*partsize+1:(part)*partsize, :);
    end
    
    DCG_SIZE = m;
    
    
    % Testing set DCG
    [~,ci] = sort(ObsFoldTest, 2, 'descend');
    ObsFoldTest_i = zeros(partsize, m);
    ObsFoldTest_rel = zeros(partsize, m);
    
    for i = 1:partsize
        rel = m;
        for ii = 1:DCG_SIZE
            ObsFoldTest_i(i, ci(i, ii)) = ii;
            ObsFoldTest_rel(i, ci(i, ii)) = rel;
            rel = rel - 1;
        end
    end
    
%      
%     % Transform to get rid of 0 entries for DCG_SIZE not equal to m
%     colsWithZeros = any(ObsFoldTest_i==0);
%     ObsFoldTest_i = ObsFoldTest_i(:, ~colsWithZeros);
    
    ObsTestDCG_R = dcg(ObsFoldTest_rel,ObsFoldTest_i); 
    

   % Training set DCG
   [~,ci] = sort(ObsFoldTrain, 2, 'descend');
   trainsize = j-partsize;
    ObsFoldTrain_i = zeros(trainsize, m);
    ObsFoldTrain_rel = zeros(trainsize, m);
    for i = 1:trainsize
        rel = m;
        for ii = 1:DCG_SIZE
            ObsFoldTrain_i(i, ci(i, ii)) = ii;
            ObsFoldTrain_rel(i, ci(i, ii)) = rel;
            rel = rel - 1;
        end
    end
    ObsTrainDCG_R = dcg(ObsFoldTrain_rel,ObsFoldTrain_i); 
   
   %Matrix Factorization of each lambda
   for a = 1:length(lambda)	% parameter selection
       fprintf("\n----------------------------------------------------\n");
       disp(part);
       disp(lambda(a));
        for b = 1:length(lambda1)
           [UU SS VV U S V] = dirtyIMC(ObsFoldTrain, XFoldTrain, Y, lambda(a), lambda1(b));
           
           %Loss for Test set
            CompletedTest =  XFoldTest*UU*SS*VV'*Y';
            [~,ci] = sort(CompletedTest, 2, 'descend');
            CompletedTest_rel = zeros(partsize, m);
            for i = 1:partsize
                rel = m;
                for ii = 1:DCG_SIZE
                    CompletedTest_rel(i, ci(i, ii)) = rel;
                    rel = rel - 1;
                end
            end
           CompletedTest_DCG_R = dcg(CompletedTest_rel, ObsFoldTest_i);
           lambdaTest_ratio(part,a) = mean(CompletedTest_DCG_R./ObsTestDCG_R);
           fprintf("\n\nTest Loss: NDCG Ratio to Ideal: %f\n", lambdaTest_ratio(part, a));
           if CompletedTest == zeros(partsize,m)
                fprintf("\n\nPROBLEM1");
                lambdaTest_ratio(part, a) = 0;
            end
           
           %Loss for Training set
            CompletedTrain =  XFoldTrain*UU*SS*VV'*Y';
            [~,ci] = sort(CompletedTrain, 2, 'descend');
            CompletedTrain_rel = zeros(trainsize, m);
            for i = 1:trainsize
                rel = m;
                for ii = 1:DCG_SIZE
                    CompletedTrain_rel(i, ci(i, ii)) = rel;
                    rel = rel - 1;
                end
            end
           CompletedTrain_DCG_R = dcg(CompletedTrain_rel, ObsFoldTrain_i);
           lambdaTrain_ratio(part,a) = mean(CompletedTrain_DCG_R./ObsTrainDCG_R);
           fprintf("Train Loss: NDCG Ratio to Ideal: %f\n", lambdaTrain_ratio(part, a));
           if CompletedTrain == zeros(trainsize,m)
                fprintf("\n\nPROBLEM2");
                lambdaTrain_ratio(part, a) = 0;
            end
           
         end
   end
end
average_lambda_ratio_test = zeros(1, length(lambda));
average_lambda_ratio_train = zeros(1, length(lambda));
for ind = 1:length(lambda)
    average_lambda_ratio_test(ind) = mean(lambdaTest_ratio(:,ind));
    average_lambda_ratio_train(ind) = mean(lambdaTrain_ratio(:,ind));
end


%Time to return values!
[best_ratioTest, best_indexTest] = max(average_lambda_ratio_test);
[best_ratioTrain, best_indexTrain] = max(average_lambda_ratio_train);
fprintf("\n\nBest Test Ratio: %f with lambda %f\n", best_ratioTest, lambda(best_indexTest));
fprintf("Best Train Ratio: %f with lambda %f\n", best_ratioTrain, lambda(best_indexTrain));
%get the average M for best lambda
[UU SS VV U S V] = dirtyIMC(Obs', X, Y, lambda(best_indexTest), lambda1);
M = UU*SS*VV';

filename = strcat("M",".mm.mtx");
mmwrite(filename,M);
filename = strcat("XR",".mm.mtx");
mmwrite(filename,XR);
filename = strcat("YR",".mm.mtx");
mmwrite(filename,YR);

end

