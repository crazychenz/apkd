import React from 'react';
import clsx from 'clsx';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import TOCItems from '@theme/TOCItems';
import styles from './styles.module.css';

const LINK_CLASS_NAME = 'table-of-contents__link toc-highlight';
const LINK_ACTIVE_CLASS_NAME = 'table-of-contents__link--active';

export default function TOC({ className, toc: autoToc, ...props }) {
  const { frontMatter } = useDoc();
  const customToc = frontMatter.custom_toc;

  const toc = customToc
    ? customToc.map(({ id, label, level = 2 }) => ({ id, value: label, level }))
    : autoToc;

  return (
    <div className={clsx(styles.tableOfContents, 'thin-scrollbar', className)}>
      <TOCItems
        {...props}
        toc={toc}
        linkClassName={LINK_CLASS_NAME}
        linkActiveClassName={LINK_ACTIVE_CLASS_NAME}
      />
    </div>
  );
}
