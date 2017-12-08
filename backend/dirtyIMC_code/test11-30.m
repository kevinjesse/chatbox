% n = 1188;
% k = 340;
% rand('seed', 0);
% randn('seed', 0);
% sparsity = 0.25;
% feature_perturb = 0.3;
% m = ceil(n^2*sparsity); % sparsity
% dim = 2*k; %WHY DO WE DO THIS

% create a real low rank matrix L 
% Tmp = randn(n, k);
% Tmp2 = randn(n, k);
% L = Tmp*Tmp2';

% optX/optY is the good feature space
% [X, ~] = qr(Tmp);
% Xorth = X(:,dim+1:end);
% optX = X(:,1:dim);
% [Y, ~] = qr(Tmp2);
% Yorth = Y(:, dim+1:end);
% optY = Y(:,1:dim);

% ii = ceil(rand(m, 1)*n);
% jj = ceil(rand(m, 1)*n);
% ind = sparse(ii, jj, 1, n, n);
% Obs = L.*(ind > 0);
% real_sparsity = nnz(Obs)/(n^2)




X = mmread("sparseXgenre.mm.mtx");
Y = mmread("sparseYgenre.mm.mtx");
Obs = mmread("sparseN.mm.mtx");

%Make full
X = full(X);
Y = full(Y);
% Obs = full(Obs');
% 
% normA = Obs - min(Obs(:));
% Obs = normA ./ max(normA(:));


disp(size(X)); % user x feature
disp(size(Y)); % movie x feature
disp(size(Obs')); % user x movie ratings

fprintf('L1\tL2\tErr\tRank(M)\tRank(N)\n')
loss = inf;
%PCA on x matrix to rank 12
approxXrank12 = pcasolver(X, 12);






%%%%% TEST 11-18-2017 %%%%%%


%Use these lambda values instead
% lambda = [70 80 90];
% lambda1 = [100000000];
% 
% %Perform Z-Score (Feature regularization for our N matrix (ratings)
% %z=(x??)/?
% %zscore with sample standard deviation, with n - 1 in the denominator 
% %of the standard deviation formula along the rows
% Obsz = zscore(Obs, 0 ,2); 
% 
% %We'll do dirtyIMC on the original Obs for comparison
% % [UU SS VV U S V] = dirtyIMC(Obs', approxXrank12, Y, lambda, lambda1);
% % CompletedObs = approxXrank12*UU*SS*VV'*Y';
% % 
% 
% 
% 
% 
% totalloss = zeros(length(lambda));
% for a = 1:length(lambda)	% parameter selection
%    	for b = 1:length(lambda1)
%    		[UU SS VV U S V] = dirtyIMC(Obsz', approxXrank12, Y, lambda, lambda1);
%   		CompletedObsZ = approxXrank12*UU*SS*VV'*Y';
%   		l = norm(Completed-Obs', 'fro')/norm(Obs, 'fro');
%   		fprintf('%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n', lambda(a), lambda1(b), l, rank(SS), rank(S));
%         total_loss(a) = l;
%         if(l < loss)
%    			loss = l;
%             best_lambda1 = lambda(a);
%    		end
%   	end
% end
% plot(lambda, total_loss, 'x-');
% % hold on;
% xlabel('Lambda Value');
% ylabel('Loss')
% 
% 









%disp(CompletedObsZ);
%%%%% End Test 11-18-2017 %%%%%

%lambda = [ 1 10 100 125.25 126];
%lambda = [125.24:.001:125.27];
%lambda = [100 105 110 115 120 125 130 135 140 145 150];
%lambda = [125.2510]
%lambda1 = [1000];




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

%[UU SS VV U S V] = dirtyIMC(ObsUser', approxXrank12 , Y, 1500, 100000000);
% totalloss = zeros(length(lambda));
% totalNDCGloss = inf;

obsf = Obs';

%appending index for cross validation shuffle
% obsf = [(1:n)' obsf];
% X = [(1:n)' X];
perm = randperm(n);
ObsShuf = obsf(perm,:);
XShuf = approxXrank12(perm,:);
% [r,idx] = sort(obsf(:
%CVO = cvpartition(obsf(:,1),'k',10);
%CO = crossvalind('Kfold',obsf,10);

start = 1;
folds=10;
if (mod(n, folds))
    return %THIS WOULD NEED a change in size of folds
end
partsize = n/folds;

   
%lambda = [1:10:131];
%lambda = [40];
lambda = [10^-3 10^-2 10^-1 1 10 100];
lambda1 = [100000000];
lambda_loss = zeros(folds,length(lambda));
lambda_ratio = zeros(folds,length(lambda));

% ObsPart = reshape(ObsShuf, partsize , [], 10);
% XPart = reshape(XShuf, partsize , [], 10);

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
    %[~,i] = sort(ObsFold, 2, 'ascend');
    [~,rel] = sort(ObsFoldTest, 2, 'descend');
    ci = (m+1)-rel;
    
    ObsDCG_R = dcg(rel,ci);
    
    %[~,Obs_DCGR_pos] = sort(ObsDCGs, 2, 'descend');
    
%     if part == start
%         ObsFold = ObsPart(:,:,start+1:fold);
%         XFold = XPart(:,:,start+1:fold);
%     elseif part == fold
%         ObsFold = ObsPart(:,:,start:fold-1);
%         XFold = XPart(:,:,start:fold-1);
%     else
%         ObsFold = [ObsPart(:,:,start:part-1),ObsPart(:,:,part+1:fold)];
%         XFold = [XPart(:,:,start:part-1) XPart(:,:,part+1:fold)];
%     end
%     
%     %Concat folds
%     ObsCat = vertcat(ObsFold(:,:,1),ObsFold(:,:,2),ObsFold(:,:,3),...
%                     ObsFold(:,:,4),ObsFold(:,:,5),ObsFold(:,:,6), ...
%                     ObsFold(:,:,7),ObsFold(:,:,8),ObsFold(:,:,9));
%     XCat = vertcat(XFold(:,:,1),XFold(:,:,2),XFold(:,:,3),...
%         XFold(:,:,4),XFold(:,:,5),XFold(:,:,6), ...
%         XFold(:,:,7),XFold(:,:,8),XFold(:,:,9));
   

%pause
   % TRAIN

   for a = 1:length(lambda)	% parameter selection
       disp(part);
       disp(lambda(a));
        for b = 1:length(lambda1)
           [UU SS VV U S V] = dirtyIMC(ObsFold, XFold, Y, lambda(a), lambda1(b));
           Completed =  XFoldTest*UU*SS*VV'*Y';
           
           [~,rel_com] = sort(Completed, 2, 'descend');
           Completed_DCG_R = dcg(rel_com, ci);
           lambda_ratio(part,a) = mean(Completed_DCG_R./ObsDCG_R);
           lambda_loss(part,a) = 1-lambda_ratio(part,a);
           fprintf("\n\nNDCG Ratio to Ideal: %f\n", lambda_ratio(part, a));
           fprintf("Loss of NDCG from Ideal: %f\n\n", lambda_loss(part, a));
           %[~,Completed_DCGR_pos] = sort(Completed_NDCG_R, 2, 'descend');
           
           %lambda_loss(part,a) =  sum(abs(normc(ObsDCGs)-normc(Completed_NDCG_R)));
           
           %loss = sum(abs(ObsDCGs-Completed_NDCG_R));
           
           %Rank Loss
           %CompletedShift = Completed - min(Completed,[],2);
           %lossNDCG = abs(1-dcg(Completed)/ObsDCGs);
            %dcgdff = abs(sum(dcg(CompletedShift),2) - sum(ObsDCGs,2));
 
 
             %lossNDCG = sum(ObsNDCG,2)-sum(CompletedNDCG,2);
 
%             if(sum(lossNDCG) < sum(totalNDCGloss))
%                 totalNDCGloss = lossNDCG;
%                 bestlambdaNDCG1 = lambda(a);
%                 bestlambdaNDCG2 = lambda(b);
%             end
% 
%             %Value loss
%             l = norm(Completed-Obs', 'fro')/norm(Obs, 'fro');
%             fprintf('%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n', lambda(a), lambda1(b), l, rank(SS), rank(S));
%             total_loss(a) = l;

%             if(l < loss)
%                 loss = l;
%                 best_lambda2 = lambda(a);
%             end
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
plot(lambda, average_lambda_ratio, 'o-');
xlabel('Lambda Value');
ylabel('NDCG Ratio to Ideal') 
hold on

% plot(lambda, average_lambda_loss, 'o-');
% xlabel('Lambda Value');
% ylabel('Loss of NDCG Ratio with Respect to Ideal') 
return

testMat = Completed + usermean' + globalmean';
% plot(lambda, total_loss, 'x-');
% % hold on;
% xlabel('Lambda Value');
% ylabel('Loss') 

%Completed = approxXrank12*UU*SS*VV'*Y';
%disp(Completed);

%%%%%%%%%% END TEST 11-20-2017 %%%%%%%%%%%




% for a = 1:length(lambda)	% parameter selection
%   	for b = 1:length(lambda1)
%           
%   		[UU SS VV U S V] = dirtyIMC(Obs', X, Y, lambda(a), lambda1(b));
%  		Completed = U*S*V'+X*UU*SS*VV'*Y';
% %  		l = norm(Completed-L, 'fro')/norm(L, 'fro');
% %  		fprintf('%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n', lambda(a), lambda1(b), l, rank(SS), rank(S));
% %   		if(l < loss)
% %   			loss = l;
% %   		end
%   	end
%  end

%fprintf('dirtyIMC: \tloss = %f\n\n', loss);
%disp(Completed)
% normA = Completed - min(Completed(:));
% Final = normA ./ max(normA(:));
% 
% disp(Final)
% max(Final(:))
% min(Final(:))
%disp(Completed);
