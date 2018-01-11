%function [M, min_lambda] = train(feature)
%TRAIN Summary of this function goes here
%   Detailed explanation goes here
feature = "genre"
if (strcmp(feature, "genre"))
     X = mmread("sparseXgenre.mm.mtx");
     Y = mmread("sparseYgenre.mm.mtx");
end

if (strcmp(feature, "mpaa"))
     X = mmread("sparseXgenre.mm.mtx");
     Y = mmread("sparseYgenre.mm.mtx");
end
% 
Obs = mmread("sparseN.mm.mtx");


%%%TEST%%%%
Obs = Obs(1:200, 1:200);
X = X(1:200, :);
Y = Y(1:200, :);


%Make full
X = full(X);
Y = full(Y);


[m,n] = size(Obs);
[j,k] = size(X);
%PCA on x matrix to rank 12
% if (strcmp(feature, "genre"))
%      X = pcasolver(X, 12, j);
% end



obsf = Obs';

%User normalization on Netflix True ratings
%sum along the columns (users) and divide by number of users (340)
%obsf = obsf./sum(obsf, 2); %m is movies, %n is users
% obsf = obsf - sum(obsf, 2)/n;
% obsf = obsf - mean(obsf(:));

perm = randperm(n);
ObsShuf = obsf(perm,:);
XShuf = X(perm,:);

start = 1;
folds=10;
if (mod(n, folds))
    return %THIS WOULD NEED a change in size of folds
end
partsize = n/folds;

%lambda = logspace(-5,5,100);
lambda = [10^-3 10^-2 10^-1 1 10 100];
%lambda = [10^-3 10^-1 10 100];
%lambda = [.9030];

lambda1 = [100000000];
lambda_loss = zeros(folds,length(lambda));
lambda_ratio = zeros(folds,length(lambda));

for part = start:folds
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
    [~,ci] = sort(ObsFoldTest, 2, 'descend');
    rel = m-ci;
    ObsDCG_R = dcg(rel,ci); 
   for a = 1:length(lambda)	% parameter selection
       disp(part);
       disp(lambda(a));
        for b = 1:length(lambda1)
           %disp(lambda1(b));
           [UU SS VV U S V] = dirtyIMC(ObsFold, XFold, Y, lambda(a), lambda1(b));
           
           CompletedTraining = XFold*UU*SS*VV'*Y';
           Completed =  XFoldTest*UU*SS*VV'*Y';
            
           [~,com_i] = sort(Completed, 2, 'descend');
           rel_com = m-com_i;
           
           Completed_DCG_R = dcg(rel_com, ci);
           lambda_ratio(part,a) = mean(Completed_DCG_R./ObsDCG_R);
           fprintf("\n\nNDCG Ratio to Ideal: %f\n", lambda_ratio(part, a));
         end
   end
end
average_lambda_ratio = zeros(1, length(lambda));
for ind = 1:length(lambda)
    average_lambda_ratio(ind) = mean(lambda_ratio(:,ind));
end

%Time to return values!
[min_lambda, min_index] = min(average_lambda_ratio);
%get the average M for best lambda
[UU SS VV U S V] = dirtyIMC(Obs', X, Y, min_lambda, lambda1);
M = UU*SS*VV';

filename = strcat(strcat("M",feature),".mm.mtx"); 
mmwrite(filename,M);
%end
