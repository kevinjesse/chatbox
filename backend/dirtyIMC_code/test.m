
feature = "genre";
X = mmread("sparseXgenre.mm.mtx");
Y = mmread("sparseYgenre.mm.mtx");
Obs = mmread("sparseN.mm.mtx");

%Make full
X = full(X);
Y = full(Y);

%PCA on x matrix to rank 12
approxXrank12 = pcasolver(X, 12);

%%%%% TEST 11-20-2017 CHO email, global->user mean %%%%%
% globalmean = mean(Obs(:));
% ObsGlobal = Obs - globalmean;
% [m,n] = size(ObsGlobal);
% usermean = (sum(ObsGlobal, 2)/ n);
% %sum along the columns (users) and divide by number of users (340)
% ObsUser = ObsGlobal - usermean; %m is movies, %n is users

%%%%%% TEST 11-29-2017 just user mean %%%%%
[m,n] = size(Obs);
[j,k] = size(X);
%usermean = (sum(Obs, 2)/ n);
%sum along the columns (users) and divide by number of users (340)
%ObsUser = Obs - usermean; %m is movies, %n is users

obsf = Obs';

%appending index for cross validation shuffle
% obsf = [(1:n)' obsf];
% X = [(1:n)' X];
perm = randperm(n);
ObsShuf = obsf(perm,:);
XShuf = approxXrank12(perm,:);

start = 1;
folds=10;
if (mod(n, folds))
    return %THIS WOULD NEED a change in size of folds
end
partsize = n/folds;

   
%lambda = logspace(-5,5,100);
lambda = [10^-3 10^-2 10^-1 1 10 100];
lambda1 = [100000000];
lambda_loss = zeros(folds,length(lambda));
lambda_ratio = zeros(folds,length(lambda));





%Completed = zeros(34,1188);

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


%     ObsFoldTest = [3, 2, 3, 0, 1, 2];
%     m = 6;
    
    [~,ci] = sort(ObsFoldTest, 2, 'descend');
    %[~,rel] = sort(ObsFoldTest, 2, 'ascend');
    
    
    rel = m-ci;
    
    ObsDCG_R = dcg(rel,ci);
   for a = 1:length(lambda)	% parameter selection
       disp(part);
       disp(lambda(a));
        for b = 1:length(lambda1)
           [UU SS VV U S V] = dirtyIMC(ObsFold, XFold, Y, lambda(a), lambda1(b));
           Completed =  XFoldTest*UU*SS*VV'*Y';
           %Completed = [0, 2, 1, 2, 3, 3];
           %Completed1 = repmat(randperm(1188,1188),34,1)
%             for i = 1:34
%                 Completed(i,:) = randperm(1188,1188);
%             end
           
           [~,com_i] = sort(Completed, 2, 'descend');
           rel_com = m-com_i;
           
           Completed_DCG_R = dcg(rel_com, ci);
           lambda_ratio(part,a) = mean(Completed_DCG_R./ObsDCG_R);
           lambda_loss(part,a) = 1-lambda_ratio(part,a);
           fprintf("\n\nNDCG Ratio to Ideal: %f\n", lambda_ratio(part, a));
           fprintf("Loss of NDCG from Ideal: %f\n\n", lambda_loss(part, a));

        end
   end
end
%Test rankings




%avgloss = bsxfun(mean,lambda_loss);
average_lambda_ratio = zeros(1, length(lambda));
average_lambda_loss = zeros(1, length(lambda));

for ind = 1:length(lambda)
    average_lambda_ratio(ind) = mean(lambda_ratio(:,ind));
    average_lambda_loss(ind) = mean(lambda_loss(:,ind));
end
plot(average_lambda_ratio, 'o-');
xticks(1:5:length(lambda))
xlabel('Lambda From Logspace')
ylabel('NDCG Ratio to Ideal')

%Time to return values!
[min_lambda, min_index] = min(average_lambda_ratio);

%get the average M for best lambda
[UU SS VV U S V] = dirtyIMC(Obs', X, Y, min_lambda, lambda1);
M = UU*SS*VV';

% plot(lambda, average_lambda_loss, 'o-');
% xlabel('Lambda Value');
% ylabel('Loss of NDCG Ratio with Respect to Ideal') 
filename = strcat(strcat("M",feature),".mm.mtx"); 
mmwrite(filename,M);
return

