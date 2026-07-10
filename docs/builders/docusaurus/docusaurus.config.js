// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';
import {visit} from 'unist-util-visit';
import {existsSync, readFileSync} from 'fs';
import {dirname, basename, extname, join} from 'path';
import yaml from 'js-yaml';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)


function remarkReplaceHiddenDivs() {
  return (tree) => {
    visit(tree, 'mdxJsxFlowElement', (node, index, parent) => {
      if (
        node.name === 'div' &&
        node.attributes?.some(
          (attr) => attr.name === 'style' && /display\s*:\s*none/i.test(attr.value)
        )
      ) {
        parent.children.splice(index, 1);
        return index;
      }
    });
  };
}



/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'APKD Docs',
  tagline: 'Android Application Analysis Documentation',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-docusaurus-site.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'thirdparty', // Usually your GitHub org/user name.
  projectName: 'apkd', // Usually your repo name.

  onBrokenAnchors: 'ignore',
  onBrokenLinks: 'ignore', //'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          //routeBasePath: '/',
          sidebarPath: './sidebars.js',
          //editUrl:
          //  'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          numberPrefixParser: false,
          remarkPlugins: [remarkReplaceHiddenDivs],
        },
        //blog: {
          // showReadingTime: true,
          // feedOptions: {
          //   type: ['rss', 'atom'],
          //   xslt: true,
          // },
          // // Please change this to your repo.
          // // Remove this to remove the "edit this page" links.
          // editUrl:
          //   'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          // // Useful options to enforce blogging best practices
          // onInlineTags: 'warn',
          // onInlineAuthors: 'warn',
          // onUntruncatedBlogPosts: 'warn',
        //},
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  markdown: {
    format: 'detect',
    parseFrontMatter: async ({filePath, fileContent, defaultParseFrontMatter}) => {
      const result = await defaultParseFrontMatter({filePath, fileContent, defaultParseFrontMatter});
      const sidecarPath = join(dirname(filePath), basename(filePath, extname(filePath)) + '.toc.yaml');
      if (existsSync(sidecarPath)) {
        const items = yaml.load(readFileSync(sidecarPath, 'utf8'));
        if (Array.isArray(items)) {
          result.frontMatter.custom_toc = items;
        }
      }
      return result;
    },
  },

  plugins: [
    function symlinkWebpackPlugin() {
      return {
        name: 'symlink-webpack-plugin',
        configureWebpack() {
          return { resolve: { symlinks: false } };
        },
      };
    },
  ],

  themes: [
    [
      "@easyops-cn/docusaurus-search-local",
      /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
      ({
        hashed: true,
        docsRouteBasePath: "/docs",
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'APKD Manual',
        // logo: {
        //   alt: 'apk logo',
        //   src: 'img/logo-dark.svg',
        // },
        items: [
          // {
          //   type: 'docSidebar',
          //   sidebarId: 'tutorialSidebar',
          //   position: 'left',
          //   label: 'Manual',
          // },
          //{to: '/blog', label: 'Blog', position: 'left'},
          // {
          //   href: 'https://github.com/facebook/docusaurus',
          //   label: 'GitHub',
          //   position: 'right',
          // },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          /*{
            title: 'Docs',
            items: [
              {
                label: 'Overview',
                to: '/0-overview',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              },
              {
                label: 'Discord',
                href: 'https://discordapp.com/invite/docusaurus',
              },
              {
                label: 'X',
                href: 'https://x.com/docusaurus',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/facebook/docusaurus',
              },
            ],
          },*/
        ],
        copyright: `Copyright © ${new Date().getFullYear()} APKD Docs. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
