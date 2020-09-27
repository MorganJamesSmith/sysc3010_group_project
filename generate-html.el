(require 'org)
(require 'ox-publish)

(setq org-publish-use-timestamps-flag nil)

(setq org-publish-project-alist
      `(("readme"
         :base-directory "."
         :publishing-directory "html"
         :headline-levels 2
         :with-broken-links t
         :with-planning t
         :html-postamble nil
         :publishing-function org-html-publish-to-html)))

(org-publish-all)
