(require 'org)
(require 'ox-publish)

(setq org-publish-use-timestamps-flag nil)

(setq org-publish-project-alist
      `(("readme"
         :base-directory "."
         :publishing-directory "html"
         :headline-levels 2
         :with-broken-links t
         :html-head-include-default-style nil
         :html-head-include-scripts nil
         :publishing-function org-html-publish-to-html)))

(org-publish-all)
