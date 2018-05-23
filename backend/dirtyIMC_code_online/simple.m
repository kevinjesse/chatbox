
feature = "genre";
X = mmread("sparseXgenre.mm.mtx"); % Load X matrix
Y = mmread("sparseYgenre.mm.mtx"); % Load Y matrix

Obs = mmread("sparseN.mm.mtx"); %read our rating matrix (R matrix)

%Make full
X = full(X);
Y = full(Y);

%Get size for future operations
[m,n] = size(Obs);  %1188 x 340
[j,k] = size(X); %340 x 22

%transpose for 340x1188 (340 users, 1188 movies)
obsf = Obs';
perm = randperm(n); %shuffle for 10-fold cross validation
ObsShuf = obsf(perm,:); %shuffled matrix with permutation
XShuf = X(perm,:); %use same permuation and shuffle user x genre

start = 1;
folds=10;
if (mod(n, folds))
    return 
end

%determine partsize and for 340 users and 10 fold is partsize of 34
partsize = n/folds; 

%choose lambda
lambda = [10^-3 10^-2 10^-1 1 10 100];
lambda1 = [100000000];

%arrays to hold our loss (ndcg ratio for each lambda)
lambda_loss = zeros(folds,length(lambda));
lambda_ratio = zeros(folds,length(lambda));

%do dirty IMC for each fold
for part = start:folds
    
    %determine the indexes of the fold and get the training and test
    %portions for each matrix Observed (R matrix) and X matrix
    if part == start
        ObsFold = ObsShuf(start*partsize+1:folds*partsize,:);
        XFold = XShuf(start*partsize+1:folds*partsize,:);
        ObsFoldTest = ObsShuf(start:start*partsize,:);
        XFoldTest = XShuf(start:start*partsize,:);
    elseif part == folds
        ObsFold = ObsShuf(start:(folds-1)*partsize, :);
        XFold = XShuf(start:(folds-1)*partsize, :);
        ObsFoldTest = ObsShuf((folds-1)*partsize+1:folds*partsize,:);
        XFoldTest = XShuf((folds-1)*partsize+1:folds*partsize,:);
    else
        ObsFold = vertcat(ObsShuf(start:(part-1)*partsize, :), ...
            ObsShuf((part*partsize)+1:folds*partsize,:));
        XFold = vertcat(XShuf(start:(part-1)*partsize, :), ...
            XShuf((part*partsize)+1:folds*partsize,:));
        
        ObsFoldTest = ObsShuf((part-1)*partsize+1:(part)*partsize, :);
        XFoldTest = XShuf((part-1)*partsize+1:(part)*partsize, :);
    end
    
    %get ideal dcg with test set
    [~,ci] = sort(ObsFoldTest, 2, 'descend');
    rel = m-ci;
    ObsDCG_R = dcg(rel,ci); 
   for a = 1:length(lambda)	% parameter selection
       disp(part);
       disp(lambda(a));
        for b = 1:length(lambda1)
           %disp(lambda1(b));
           %do dirty IMC on training set
           [UU SS VV U S V] = dirtyIMC(ObsFold, XFold, Y, lambda(a), lambda1(b));
           
           %get completed from test
           Completed =  XFoldTest*UU*SS*VV'*Y';
            
           %get dcg with completed
           [~,com_i] = sort(Completed, 2, 'descend');
           rel_com = m-com_i;
           Completed_DCG_R = dcg(rel_com, ci);
           
           %compute NDCG
           lambda_ratio(part,a) = mean(Completed_DCG_R./ObsDCG_R);
           fprintf("\n\nNDCG Ratio to Ideal: %f\n", lambda_ratio(part, a));
         end
   end
end

%compute the average loss across all 10 folds for each lambda
average_lambda_ratio = zeros(1, length(lambda));
for ind = 1:length(lambda)
    average_lambda_ratio(ind) = mean(lambda_ratio(:,ind));
end

%Time to return values!
[min_lambda, min_index] = min(average_lambda_ratio); %return the best lambda
%get the average M for best lambda
[UU SS VV U S V] = dirtyIMC(Obs', X, Y, min_lambda, lambda1);
M = UU*SS*VV';

filename = strcat(strcat("M",feature),".mm.mtx"); 
mmwrite(filename,M);